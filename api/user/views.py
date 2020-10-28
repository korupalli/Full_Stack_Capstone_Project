from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.serializers import UserRegistrationSerializer
from user.serializers import UserLoginSerializer
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from profile.models import UserProfile
from movie_review.models import movies,reviews
import requests
from collections import defaultdict
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from profile.models import UserProfile
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime

'''
Json input format for user registration. Do not change genres and languages inside profile
{
    "email":"123@gmail.com",
    "password":"rohithkorupalli",
    "genre":["Horror","Action"],
    "Language":["Chinlish","Hindi"],
    "profile": 
        {
            "firstname":"rohith",
            "lastname":"korupalli",
            "username":"roko123",
            "gender":"Male",
            "genres":"",
            "languages":"English"
        }
}
'''


#global search_static

@api_view(['POST', ])
def UserRegistrationView(request):
    if request.method == 'POST':
        serializer_class = UserRegistrationSerializer
        permission_classes = (AllowAny,)

        #print(request.data)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            'success' : 'True',
            'statusCode' : status.HTTP_200_OK,
            'message': 'User registered  successfully',
            }
        statusCode = status.HTTP_200_OK
        #print(response)
        return Response(response, status=statusCode)


@api_view(['POST', ])
def UserLoginView(request):
    #print(request.data)
    context = {}
    email = request.data['email']
    password = request.data['password']
    #print(email,password)
    user = authenticate(request,email=email, password=password)
    if user is None:
            context['response'] = 'A user with this email and password is not found.'
    #if user.DoesNotExist:
     #   context['response'] = 'User with given email and password does not exists'
    else:
        user_profile = UserProfile.objects.get(user=user)
        context['response'] = {
                'success' : 'True',
                'statusCode' : status.HTTP_200_OK,
                'message': 'User logged in  successfully',
                'id':str(user_profile),
				'email':email,
                'firstname':user_profile.firstname,
                'lastname':user_profile.lastname,
		        'username':user_profile.username,
                'profilePic':user_profile.profilePic
                }
    statusCode = status.HTTP_200_OK
    return Response(context, status=statusCode)
    #return Response(context)


def searchpage(b):
            #if len(search_static) == 0:
                search_page = defaultdict(list)
                for i in range(1,11):
                    nav_search=defaultdict(list)
                    res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page='+str(i)+'&release_date.gte=2014-01-01')
                #try:
                    nav_search['result'].extend(res.json()['results'])
                    y_search=search_func(nav_search,'search_bar')
                    if len(y_search) !=0:
                            search_page['name_results'].extend(y_search['navbar_result'])
                #except KeyError:
                        #continue
                search_page['name_results'].sort(key=lambda x: datetime.strptime(x['release_date'], '%Y-%m-%d'), reverse=True)
            #print(len(search_page['name_results']))
                #search_static=search_page
                print(search_page)
                if b == 'browse':
                    search_page['name_results'] = sorted(search_page['name_results'], key=lambda k: ( -k['rating'],k['title'].lower()))
                search_page=json.dumps(search_page)
                return JsonResponse(json.loads(search_page),safe=False)
            #else:
                 #search_static=json.dumps(search_static)
                 #return JsonResponse(json.loads(search_static),safe=False)


def get_review(user,id,final):
    final['review_id']=[]
    final['review']=[]
    final['user']=[]
    final['rating']=[]
    final['watched'] = False
    final['liked'] = False
    final['wishlist'] = False
    final['time']=[]
    final['date']=[]
    final['upvote']=[]
    final['downvote']=[]
    final['follow']=[]
    #final['review_id']=[]
    for i in reviews.objects.filter(movie__movie_id=id):
        if i.review != "":
           final['review_id'].append(i.id)
           final['review'].append(i.review)
           final['user'].append(i.review_user_id)
           final['rating'].append(i.rating)
           final['time'].append(i.review_time)
           final['date'].append(i.review_date)
           final['upvote'].append(i.upvote_count)
           final['downvote'].append(i.downvote_count)
           final['follow'].append(i.follow)
        #final['review_id'].append(i.id)
    #print(final)
    if user == 'Guest':
        final['watched']= False
        final['liked']=False
        final['wishlist']=False
    else:
        #print("yup")
        #data=serializers.serialize("json", reviews.objects.all(),indent=4 )
        #print(id)
        #print(user)
        for i in reviews.objects.filter(movie__movie_id=id , review_user_id=user):
            #print("entered")
            final['watched'] = i.watched
            final['liked'] = i.liked
            final['wishlist'] = i.wishlist
    return final



class Homepage(APIView):
    def post(self, request):
            required=['popular','top_rated','now_playing']
            #Tmdb provides maximum of 20 results for each page and we can't send Multiple page requests in single Query so using For loop
            intial_homepage=defaultdict(list)
            final_homepage=defaultdict(list)
            poster_url='http://image.tmdb.org/t/p/original/'
            for i in range(1,4):
                for j in required:
                    url='https://api.themoviedb.org/3/movie/'+j+'?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&page='+str(i)
                    response=requests.get(url)
                    intial_homepage[j].extend(response.json()['results'])
            #intial_homepage consistis of all the details of movies returned from the movie , but we require only ID, RELASEDATE , POSTER, DESCRIPTION, TITLE of every movie in each Required list. so forming our final home_page
            #Rating is given out of 10, so for this project rating is maintained in between 0 to 5
            for i in required:
                for j in range(0,50):
                    d={}
                    d['id']=intial_homepage[i][j]['id']
                    d['title']=intial_homepage[i][j]['title']
                    d['rating']=round((intial_homepage[i][j]['vote_average'])/2,1)
                    d['description']=intial_homepage[i][j]['overview']
                    if intial_homepage[i][j]['poster_path'] is None:
                        d['poster']='https://i.stack.imgur.com/Q3vyk.png'
                    else:
                        d['poster']=poster_url+intial_homepage[i][j]['poster_path']
                    d['release_date']=intial_homepage[i][j]['release_date']
                    final_homepage[i].append(d)
            final_homepage['now_playing'].sort(key= lambda x : datetime.strptime(x['release_date'],'%Y-%m-%d'),reverse=True)
            home_page=json.dumps(final_homepage)
            return JsonResponse(json.loads(home_page), safe=False)

#request should be "https://127.0.0.1:8000/api/search/?query='movie name'

def search_func(resp, n):
    final_resp = defaultdict(list)
    poster_url = 'http://image.tmdb.org/t/p/original/'
    for i in resp['result']:
        d = {}
        d['id'] = i['id']
        d['title'] = i['title']
        d['rating'] = round(i['vote_average'] / 2, 1)
        d['description'] = i['overview']
        if i['poster_path'] is None:
            d['poster'] = 'https://i.stack.imgur.com/Q3vyk.png'
        else:
            d['poster'] = poster_url + i['poster_path']
        try:
            d['release_date']=i['release_date']
        except KeyError:
            d['release_date']=0
        if n == 'genre':
            final_resp['genre_result'].append(d)
        elif n=='name':
            final_resp['name_result'].append(d)
        elif n=='desc':
            final_resp['description_result'].append(d)
        elif n=='search_bar':
            final_resp['navbar_result'].append(d)
        else:
            final_resp['browse_result'].append(d)
    return final_resp

def simple_get(url):
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
                                                                Chrome/77.0.3865.90 Safari/537.36'}
        with closing(get(url,stream = True,headers=header)) as resp:
            if 'html' in resp.headers['Content-Type'] and resp.statusCode == 200:
                return resp.content
            else:
                return None
    except RequestException:
        #print(f'Request for {url} failed')
        return None

class MovieSearch(APIView):
    def post(self, request):
        query=request.GET.get('query', '')
        if len(query) !=0:
            query_list = query.split()
        #print(query_list)
            genre = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US")
            genre_list = genre.json()['genres']
        #print(genre_list)
            genre_id = []
            for q in query_list:
            #print("q is",q)
                 for genre in genre_list:
                #print("q in",q.lower())
                #print("name is ",genre['name'].lower())
                    if q.lower() == genre['name'].lower():
                         #print("entrered")
                         genre_id.append(genre['id'])
                         break
        #print("genre",genre_id)
            if len(genre_id) >= 1:
                #print("entered")
                res = requests.get("https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=true&page=1" + "&with_genres=" + str(genre_id[0]))
                if res.json()['total_pages'] > 4:
                    pages = 4
                elif res.json()['total_pages'] < 4 and res.json()['total_pages'] != 0:
                    pages = res.json()['total_pages']
                else:
                    pages = 2
                genre_resp = defaultdict(list)
                for i in range(1, pages):
                      url = "https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=true&page=" + str(
                i) + "&with_genres=" + str(genre_id[0])
                      response = requests.get(url)
                      genre_resp['result'].extend(response.json()['results'])
                genre_search = search_func(genre_resp, "genre")
            else:
                genre_search = defaultdict(list)
            if len(query) >= 1:
                initial_search = defaultdict(list)
                res = requests.get('https://api.themoviedb.org/3/search/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&query=' + str(query) + '&page=1' +'&sort_by=popularity.desc'+ '&include_adult=false')
                if res.json()['total_pages'] > 4:
                    pages = 4
                elif res.json()['total_pages'] < 4 and res.json()['total_pages'] != 0:
                    pages = res.json()['total_pages']
                else:
                    pages = 2
                for i in range(1, pages):
                     url = 'https://api.themoviedb.org/3/search/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&query=' + str(query) + '&page=' + str(i)+'&sort_by=popularity.desc' + '&include_adult=false'
                     response = requests.get(url)
                     initial_search['result'].extend(response.json()['results'])
                     name_search = search_func(initial_search, "name")
            else:
                name_search = defaultdict(list)
            s = BeautifulSoup(simple_get('https://www.whatismymovie.com/results?text='+query), 'html.parser')
            desc_movies=[]
            for heading in s.find_all(["h3"]):
            #print(s)
                if heading.text.strip().endswith(')'):
                    x=len(heading.text.strip())
                if heading.text.strip()[:x-7] not in desc_movies:
                    desc_movies.append(heading.text.strip()[:x-7])
            description_search = defaultdict(list)
        #print(desc_movies)
            for i in desc_movies[:30]:
                initial_search = defaultdict(list)
                res = requests.get('https://api.themoviedb.org/3/search/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&query=' + str(i)+'&sort_by=popularity.desc' + '&page=1' + '&include_adult=false')
            #print(res.json())
                try:
                    if res.json()['total_pages'] > 4:
                        pages = 4
                    elif res.json()['total_pages'] < 4 and res.json()['total_pages'] != 0:
                        pages = res.json()['total_pages']
                    else:
                        pages = 2
                    for i in range(1, pages):
                         initial_search['result'].extend(res.json()['results'])
                    x_search = search_func(initial_search, "desc")
                #print(x_search)
                    if len(x_search) !=0:
                        description_search['description_result'].extend(x_search['description_result'])
                except KeyError:
                    continue
            search_page = dict(list(genre_search.items()) + list(name_search.items())+ list(description_search.items()))
            search_page = json.dumps(search_page)
            return JsonResponse(json.loads(search_page), safe=False)
        else:
            return searchpage('search')


class MovieDetails(APIView):
    def post(self, request):
        id=request.data['id']
        #print("id received",id)
        user=request.data['user']
        youtube_path="https://www.youtube.com/watch?v="
        poster_url = 'http://image.tmdb.org/t/p/original/'
        if id != 0:
            movie_details=defaultdict(list)
            url='https://api.themoviedb.org/3/movie/'+str(id)+'?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&append_to_response=credits,videos'
            response=requests.get(url)
            movie_details['id']=response.json()['id']
            movie_details['imdb_rating']=round((response.json()['vote_average'])/2,1)
            movie_details['description']=response.json()['overview']
            movie_details['title']=response.json()['title']
            if response.json()['poster_path'] is None:
                movie_details['poster'] = 'https://i.stack.imgur.com/Q3vyk.png'
            else:
                movie_details['poster'] = poster_url + response.json()['poster_path']
            for i in range(len(response.json()['genres'])):
                 movie_details['genres'].append(response.json()['genres'][i]['name'])
            for i in range(len(response.json()['videos']['results'])):
                    if response.json()['videos']['results'][i]['type'] == 'Trailer' :
                         movie_details['trailers'].append(youtube_path+str(response.json()['videos']['results'][i]['key']))
            for i in range(len(response.json()['videos']['results'])):
                    if response.json()['videos']['results'][i]['type'] == 'Teaser' :
                         movie_details['teasers'].append(youtube_path+str(response.json()['videos']['results'][i]['key']))
            for i in range(len(response.json()['credits']['cast'])):
                    if i<10:
                           movie_details['cast'].append(response.json()['credits']['cast'][i]['name'])
                    else:
                        break

            for i in range(len(response.json()['credits']['crew'])):
                      if response.json()['credits']['crew'][i]['job'] == 'Director':
                               movie_details['director'].append(response.json()['credits']['crew'][i]['name'])
                      if response.json()['credits']['crew'][i]['job'] == 'Producer':
                               movie_details['producer'].append(response.json()['credits']['crew'][i]['name'])
            movie_details['release_date']=response.json()['release_date']
            if not(movie_details['trailers']):
                        movie_details['trailers'].append(None)
            if not(movie_details['teasers']):
                        movie_details['teasers'].append(None)
            reviews = get_review(user, id,movie_details)
            #if user == 'Guest':
            details_page = json.dumps(reviews,default=str)
            return JsonResponse(json.loads(details_page), safe=False)
        else:
            return redirect('/homepage')


class MovieBrowse(APIView):
    def post(self,request):
        #print("request",request.data)
        genre_given=False
        director_given=False
        if len(request.data.keys()) > 0:
             genre_id=[]
             director=[]
             genre=''
             dir=''
             #print(list(request.data.keys()))
             for i in request.data.keys():
                #print(i)
                if i == 'genre_id':
                    genre_id=request.data['genre_id']
                else:
                     director=request.data['director_id']
             #print(genre_id)
             #print(director)
             if len(genre_id) !=0:
                genre +='|'.join(map(str, genre_id))
             if len(director) !=0:
                 dir +='|'.join(map(str, director))
             #print("dir is",dir)
             browse_resp = defaultdict(list)
             if len(genre)>0 and len(dir)>0:
                director_given=True
                genre_given=True
                res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page=1&with_crew='+dir+'&with_genres='+genre)
                for i in range(1,res.json()['total_pages']+1):
                    #print(i)
                    if i>10:
                          break
                    res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page='+str(i)+'&with_crew='+dir+'&with_genres='+genre)
                    browse_resp['result'].extend(res.json()['results'])
             elif len(genre)>0 :
                genre_given=True
                res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=vote_average.desc&include_adult=false&include_video=false&page=1&with_genres='+genre)
                for i in range(1,res.json()['total_pages']+1):
                    #print(i)
                    if i>10:
                          break
                    res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(i)+'&with_genres='+genre)
                    browse_resp['result'].extend(res.json()['results'])
                    
                #browse_search = search_func(browse_resp,'browse')
             else:
                director_given=True
                res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_crew='+dir)
                for i in range(1,res.json()['total_pages']+1):
                    if i>10:
                          break
                    res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=c8b243a9c923fff8227feadbf8e4294e&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(i)+'&with_crew='+dir)
                    browse_resp['result'].extend(res.json()['results'])

             browse_search = search_func(browse_resp,'browse')
             if genre_given and director_given:
                     browse_search['browse_result'] = sorted(browse_search['browse_result'], key=lambda k: ( -k['rating'],k['title'].lower()))
             elif genre_given :
                     browse_search['browse_result'] = sorted(browse_search['browse_result'], key=lambda k: ( -k['rating'],k['title'].lower()))
                     browse_search['genre_result']=browse_search['browse_result']
                     del browse_search['browse_result']
             else:
                browse_search['browse_result'] = sorted(browse_search['browse_result'], key=lambda k: ( -k['rating'],k['title'].lower()))
                browse_search['director_result']=browse_search['browse_result']
                del browse_search['browse_result']
             browse_search=json.dumps(browse_search)
             return JsonResponse(json.loads(browse_search), safe=False)
        else:
             return searchpage('browse')


