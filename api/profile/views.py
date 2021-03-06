from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from profile.models import UserProfile
from movie_review.helper import get_movie_details
from movie_review.models import reviews
from user.models import User
from notifications.models import notifications
import datetime
from collections import defaultdict
import random

statusCode = status.HTTP_400_BAD_REQUEST
RESPONSE = {
    'success': 'false',
    'status code': status.HTTP_400_BAD_REQUEST,
    'message': 'User does not exists',
    }

pictures = {'Female': ['https://react.semantic-ui.com/images/avatar/small/elliot.jpg',
'https://react.semantic-ui.com/images/avatar/small/jenny.jpg'],
'Male': ['https://react.semantic-ui.com/images/avatar/small/matt.jpg',
'https://react.semantic-ui.com/images/avatar/small/joe.jpg']}

#post for viewing user profile and put edits profile
class UserProfileView(RetrieveAPIView):
    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(username=request.data['username'])
            statusCode = status.HTTP_200_OK
            User1=User.objects.get(id=user_profile.user_id)
            response = {
                'success': 'true',
                'status code': statusCode,
                'message': 'User profile fetched successfully',
                'data': {
                    'firstname': user_profile.firstname,
                    'lastname': user_profile.lastname,
                    'gender': user_profile.gender,
                    'genres':user_profile.genres,
                    'languages':user_profile.languages,
                    'profilePic':user_profile.profilePic,
                    'email': User1.email
                }}
        except Exception as e:
            RESPONSE['error']= str(e)
            return Response(RESPONSE, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=statusCode)

    def put(self, request, *args, **kwargs):
        #print('PUT called ',request.data)
        try:
            user_profile = UserProfile.objects.get(username=request.data['username'])

            if 'firstname' in request.data.keys():
                user_profile.firstname = request.data['firstname']
            if 'lastname' in request.data.keys():
                user_profile.lastname = request.data['lastname']
            if 'gender' in request.data.keys():
                user_profile.gender = request.data['gender']
            if 'genres' in request.data.keys():
                user_profile.genres = request.data['genres']
            if 'languages' in request.data.keys():
                user_profile.languages = request.data['languages']
            if 'profilePic' in request.data.keys():
                user_profile.profilePic = request.data['profilePic']
            user_profile.save()
            statusCode = status.HTTP_200_OK
            response = {
                'success': 'true',
                'statusCode': statusCode,
                'message': 'User profile updates successfully',
                'data': {
                    'firstname': user_profile.firstname,
                    'lastname': user_profile.lastname,
                    'gender': user_profile.gender,
                    'genres':user_profile.genres,
                    'languages':user_profile.languages,
                    'profilePic':user_profile.profilePic}}
        except Exception as e:
            RESPONSE['error']= str(e)
            return Response(RESPONSE, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=statusCode)

#put for banning a user and post for seeing banned users
class BanView(RetrieveAPIView):
    def put(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(username=request.data['username'])
        if request.data['banStatus'] and request.data['bannedUsername'] not in user_profile.banned:
            user_profile.banned.append(request.data['bannedUsername'])
            if request.data['bannedUsername'] in list(user_profile.following):
                user_profile.following.remove(request.data['bannedUsername'])
            message = 'user banned'
        elif request.data['banStatus']==False and request.data['bannedUsername'] in user_profile.banned:
            user_profile.banned.remove(request.data['bannedUsername'])
            message = 'user unbanned'
        else:
            response = {
            'success': 'true',
            'statusCode': status.HTTP_200_OK,
            'message': 'doubled request',
            'data': {
                'banned':user_profile.banned}}
            return Response(response, status=status.HTTP_200_OK)
        user_profile.save()
        statusCode = status.HTTP_200_OK
        response = {
            'success': 'true',
            'statusCode': statusCode,
            'message': message,
            'data': {
                'banned':user_profile.banned}}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(username=request.data['username'])
        response = {
            'success': 'true',
            'data': []}
        for i in list(user_profile.banned):
            user = UserProfile.objects.get(username=i)
            response['data'].append({
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'gender': user.gender,
                    'profilePic':user.profilePic,
                    'username':i
                })

        return Response(response, status=status.HTTP_200_OK)

#put for adding to watchlist and post for seeing watchlist
class watchlistView(RetrieveAPIView):
    def put(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(username=request.data['username'])
        try:
            movie_review = reviews.objects.get(movie_id=request.data['movieID'] , review_user_id=request.data['username'])
        except Exception:
            movie_review = reviews()
            movie_review.movie_id = request.data['movieID']
            movie_review.review_user_id = request.data['username']
        #print('-----------------########',movie_review)
        if request.data['movieStatus'] and str(request.data['movieID']) not in user_profile.watched:
            #print('yes')
            user_profile.watched.append(request.data['movieID'])
            movie_review.watched = True
            movie_review.save()
            message = 'movie watched'
        elif request.data['movieStatus']==False and str(request.data['movieID']) in user_profile.watched:
            user_profile.watched.remove(str(request.data['movieID']))
            movie_review.watched = False
            movie_review.save()
            message = 'Movie unwatched'
        else:
            response = {
            'success': 'true',
            'statusCode': status.HTTP_200_OK,
            'message': 'doubled request',
            'data': {
                'watchlist':list(map(int, list(user_profile.watched)))}}
            return Response(response, status=status.HTTP_200_OK)
        user_profile.save()
        statusCode = status.HTTP_200_OK
        response = {
            'success': 'true',
            'statusCode': statusCode,
            'message': message,
            'data': {
                'watchlist':list(map(int, list(user_profile.watched)))}}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(username=request.data['username'])
        response = {
            'success': 'true',
            'data': []}
        for movie in list(map(int, list(user_profile.watched))):
            response['data'].append(get_movie_details(movie))
        return Response(response, status=status.HTTP_200_OK)

#put for following user and post for seeing follwed users
class followUser(RetrieveAPIView):
    def put(self, request, *args, **kwargs):
        follower = UserProfile.objects.get(username=request.data['follower'])
        followee = UserProfile.objects.get(username=request.data['followee'])
        message = ''
        print(request.data['follower'],request.data['followee'])
        print(followee.followed_by,follower.following)
        if str(request.data['follower']) in followee.followed_by and str(request.data['followee']) in follower.following:
            response = {
            'success': 'false',
            'statusCode': statusCode,
            'message': 'Already added'}
            return Response(response, status=status.HTTP_200_OK)
        if str(request.data['follower']) not in followee.followed_by:
            followee.followed_by.append(str(request.data['follower']))
            followee.save()
            message += 'follower added'

        if str(request.data['followee']) not in follower.following:
            follower.following.append(str(request.data['followee']))
            follower.save()
            message += ' & followee added'

        '''new = notifications()
        new.toUsername = request.data['followee']
        new.fromUsername = request.data['follower']
        new.type = request.data['follower'] + ' is following you'
        new.Date = datetime.date.today()
        new.Time = datetime.datetime.now().time()
        new.save()'''
        response = {
            'success': 'true',
            'statusCode': status.HTTP_200_OK,
            'message': message}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(username=request.data['userID'])
        data = []
        for user in userprofile.following:
            new_user = UserProfile.objects.get(username=user)
            user_data = defaultdict(lambda: None)
            user_data['username'] = user
            user_data['profilePic'] = new_user.profilePic
            user_data['firstname'] = new_user.firstname
            user_data['lastname'] = new_user.lastname
            data.append(user_data)

        response = {
            'success': 'true',
            'statusCode': status.HTTP_200_OK,
            'following':data
        }
        return Response(response, status=status.HTTP_200_OK)

#put unfollws user
class unfollowUser(RetrieveAPIView):
    def put(self, request, *args, **kwargs):
        follower = UserProfile.objects.get(username=request.data['follower'])
        followee = UserProfile.objects.get(username=request.data['followee'])

        if str(request.data['follower']) in followee.followed_by or str(request.data['followee']) in follower.following:
            followee.followed_by.remove(str(request.data['follower']))
            followee.save()

            follower.following.remove(str(request.data['followee']))
            follower.save()

        response = {
        'success': 'true',
        'statusCode': status.HTTP_200_OK,
        'message': 'Unfollowed'}
        return Response(response, status=status.HTTP_200_OK)
