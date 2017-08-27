from scraper import get_game_review, get_latest_games_reviewed, get_releases
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

##########################################
# GAME REVIEWS
##########################################

@app.route('/games/<game>')
def game_review(game):
  return jsonify(get_game_review(game))


##########################################
# LATEST GAMES REVIEWED
##########################################

@app.route('/latest-games-reviewed')
@app.route('/latest-games-reviewed/<platform>')
def latest_games_reviewed(platform="all"):
  limit = request.args.get("limit")
  if limit:
    return jsonify(get_latest_games_reviewed(platform, limit))
  else:
    return jsonify(get_latest_games_reviewed(platform, limit=5))


##########################################
# RELEASES
##########################################
@app.route('/releases')
@app.route('/releases/<year>/<month>')
@app.route('/releases/<year>/<month>/<platform>')
def releases(platform="all", year=datetime.now().year, month=datetime.now().month):
  return jsonify(get_releases(platform, year, month))

##########################################
# START FLASK
##########################################

if __name__ == '__main__':
    app.run(port=5000, debug=True)