import React from 'react';
import{
  BrowserRouter as Router,
  Route,
  Switch,
} from 'react-router-dom';
import './App.css';
import NotFoundPage from './pages/NotFoundPage';
import SignUpPage from './pages/SignUpPage';
import MovieDetails from './pages/MovieDetails'
import HomePage from './pages/HomePage';
import Login from './pages/Login';
import RecentReleased from './pages/RecentReleased';
import TopRated from './pages/TopRated';
import PopularMovies from './pages/PopularMovies';
import WishListPage from './pages/WishListPage';
import SearchPage from './pages/SearchPage';
import SearchMovieTitle from './pages/SearchMovieTitle';
import SearchGenre from './pages/SearchGenre';
import SearchDescription from './pages/SearchDescription';
import ProfilePage from './pages/ProfilePage';
import WatchListPage from './pages/WatchListPage';
import BannedUsers from './pages/BannedUsers';
import Browse from './pages/Browse';
import SignUp from './pages/SignUp';
function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" component={HomePage} exact/>
        <Route path="/recentReleased" component={RecentReleased} exact/>
        <Route path="/topRated" component={TopRated} exact/>
        <Route path="/popularMovies" component={PopularMovies} exact/>
        <Route path="/welcome" component={HomePage} />
        <Route path="/browse" component = {Browse} />
        <Route path="/wishlist/:userId" component={WishListPage} />
        <Route path="/watchlist/:userId" component={WatchListPage} />
        <Route path="/bannedlist/:userId" component={BannedUsers} />
        <Route path="/myprofile" component = {ProfilePage} />
        <Route path="/login" component = {Login} />
        <Route path="/signup" component = {SignUp} />
        <Route path="/search/:searchText" component = {SearchPage} />
        <Route path="/searchMovieTitle" component = {SearchMovieTitle} />
        <Route path="/searchGenre" component = {SearchGenre} />
        <Route path="/searchDescription" component = {SearchDescription} />
        <Route path="/movieDetails/:movieId" component = {MovieDetails} />
        <Route component = {NotFoundPage} />
      </Switch>
    </Router>
  );
}

export default App;
