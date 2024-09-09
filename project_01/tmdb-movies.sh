#!/bin/bash

#1. order by release_date desc
csvsort tmdb-movies.csv -c release_date -r > 1-tmdb-movies.csv

#2. filter movies where rating > 7.5
csvsql tmdb-movies.csv --query "SELECT * FROM 'tmdb-movies' WHERE vote_average > 7.5" > 2-tmdb-movies.csv

#3.movie with highest revenue
csvsql tmdb-movies.csv --query "SELECT * FROM 'tmdb-movies' WHERE revenue = (SELECT MAX(revenue) FROM 'tmdb-movies')" > 3-tmdb-movies.csv

#4. sum revenue
csvsql tmdb-movies.csv --query "SELECT SUM(revenue) FROM 'tmdb-movies'" > 4-tmdb-movies.csv

#5. top 10 most profitable movies
csvcut -c genres tmdb-movies.csv | tr "|" "\n" > tmp-7-tmdb-movies.csvzcsvsql tmdb-movies.csv --query "SELECT original_title, revenue - budget AS profit FROM 'tmdb-movies' ORDER BY profit DESC LIMIT 10" > 5-tmdb-movies.csv

#6. which director, actor has the most movies
csvcut -c director tmdb-movies.csv -x | tr -d "," | tr -d '"' | tr "|" "\n" > tmp-6-tmdb-movies.csv

csvsql tmp-6-tmdb-movies.csv --query "SELECT director, COUNT(*) FROM 'tmp-6-tmdb-movies' GROUP BY director ORDER BY COUNT(*) DESC LIMIT 1"

#7. genres
csvcut -c genres tmdb-movies.csv | tr "|" "\n" > tmp-7-tmdb-movies.csv

csvsql tmp-7-tmdb-movies.csv --query "SELECT genres, COUNT(*) FROM 'tmp-7-tmdb-movies' GROUP BY genres ORDER BY COUNT(*) DESC"
