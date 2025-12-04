from flask import Flask, redirect, url_for, render_template, request, session
import os
import json
import uuid
from game.game import Game
from game.team import Team

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # Set a unique and secret key for session management

@app.route('/')
def home():
    return redirect(url_for('start_game'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/start_game', methods=['GET', 'POST'])
def start_game():
    
    session.clear()  # 🧹 wipe previous data

    if request.method == 'POST':
        team_name = request.form['team_name']
        # rounds = int(request.form['total_rounds'])
        rounds = 5
        sprints_per_round = 4  # fixed for now
        session["team_id"] = str(uuid.uuid4())
        session['team_name'] = team_name
        session['total_rounds'] = rounds
        session['sprints_per_round'] = sprints_per_round  # fixed for now
        return redirect(url_for('play_sprint', sprint_num = 0))
    
    return render_template('start_game.html')



@app.route('/play_sprint/<int:sprint_num>', methods=['GET', 'POST'])
def play_sprint(sprint_num):

    team_name = session['team_name'] 
    # redirect if name was not set
    if not team_name:
        return redirect(url_for('start_game')) 
    
    if 'team_data' in session:
        # after 1st sprint, load team and game state from session
        team = Team.from_dict(session['team_data'], current_sprint = sprint_num)
        # Load previous game state 
        game = Game.from_dict(session['game_data'], team = team)

    else:
        # Before the very 1st sprint, initialize team and game
        team = Team(team_name)
        game = Game(team, sprints_per_round = session['sprints_per_round'], total_sprints = session['total_rounds'] * session['sprints_per_round'])
        # Save initial game state in session
        session['game_data'] = game.to_dict()
        # Update team state in session
        session['team_data'] = team.to_dict()

    round_num = sprint_num // game.sprints_per_round + 1
    sprint_in_round = sprint_num % game.sprints_per_round + 1
    error = None
    # Get sprint and round messages from session if they exist
    sprint_message = session.pop('sprint_message', None)
    round_message = session.pop('round_message', None)

    if request.method == 'POST':
        try:
            ##### sprint play logic
            allocations = {
                'New feature': int(request.form.get('feature', 0)),
                'Optimization':  int(request.form.get('optimization')),
                'Testing':  int(request.form.get('testing', 0)),
                'Bug resolution':  int(request.form.get('bugfix', 0)),
                'Technical debt':  int(request.form.get('technical_debt', 0))
            }

            staffing = { 
                'Hire developers':  int(request.form.get('hire_developers', 0))
            }

            game.play_sprint(sprint_num, allocations = allocations, staffing = staffing, current_sprint = sprint_num)

            ##### end sprint and post sprint message
            met_expectations, too_much_debt = game.end_sprint()
            sprint_message = sprint_message_text(met_expectations, too_much_debt)
            session['sprint_message'] = sprint_message
            # Increase expectation for the next sprint
            game.expectation['feature'] += 1 * ((sprint_num + 1) % 2)
            game.expectation['optimization'] += 1 * ((sprint_num + 2) % 2)

            ##### Sprint/Round/Game end logic ####
            if (sprint_num + 1) >= game.total_sprints:
                ### game end
                game.end_round()
                game.end_game()
                # Update team state in session
                session['team_data'] = team.to_dict()
                return redirect(url_for('end_game'))
            
            elif (sprint_num + 1) % game.sprints_per_round == 0:
                ### round end   
                met_expectations, too_many_bugs = game.end_round()
                round_message = round_message_text(too_many_bugs)
                session['round_message'] = round_message

                # Save round results to a separate file
                filename = "results_round_" + str(round_num) + ".json"
                save_to_json(team, filename)
                # Update team and game state in session
                session['game_data'] = game.to_dict()
                session['team_data'] = team.to_dict()
                return redirect(url_for('end_round', round_num = round_num, sprint_num = sprint_num))
            
            else:
                # regular sprint end
                # Update team state in session
                session['team_data'] = team.to_dict()
                session['game_data'] = game.to_dict()
                return redirect(url_for('play_sprint', sprint_num = sprint_num + 1))
            
        except ValueError as e:
            error = str(e)    

    return render_template(
        'play_sprint.html', game=game, sprints_per_round=game.sprints_per_round,
        sprint_in_round=sprint_in_round, round_num=round_num, sprint_num = sprint_num, rounds=session['total_rounds'],
        team=team, error=error, round_message=round_message, sprint_message=sprint_message
    )

@app.route('/end_round/<int:round_num>/<int:sprint_num>', methods=['GET', 'POST'])
def end_round(round_num, sprint_num):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filename = "results_round_" + str(round_num) + ".json"
    ROUND_RESULTS_FILE = os.path.join(BASE_DIR, filename)

    # Load results
    if os.path.exists(ROUND_RESULTS_FILE):
        with open(ROUND_RESULTS_FILE, "r") as f:
            results = json.load(f)
    else:
        results = []

    my_result = [result for result in results if result['team_id'] == session["team_id"]][0]
    # ✅ Sort: high satisfaction, then fewer bugs, then fewer technical debt
    results.sort(
        key=lambda r: (-r["satisfaction"], r["bugs"], r["technical_debt"])
    )
 
    return render_template('end_round.html', my_result=my_result, results=results, sprint_num = sprint_num)       

@app.route('/end_game', methods=['GET', 'POST'])
def end_game():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_FILE = os.path.join(BASE_DIR, "results.json")

    team_name = session.get('team_name')
    if not team_name:
        return redirect(url_for('start_game'))
    if request.method == 'POST':
        return redirect(url_for('start_game'))
    
    team = Team.from_dict(session['team_data'])

     # Load existing results
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            results = json.load(f)
    else:
        results = []

     # Save current team result
    result_entry = {
        "team": team.name,
        "satisfaction": team.satisfaction,
        "features": team.total_features,
        "optimizations": team.total_optimizations,
        "bugs": team.bugs,
        "technical_debt": team.technical_debt,
        "resources": team.resources,
        "team_id": str(uuid.uuid4())  # Unique ID for the result
    }

    # Append new result
    results.append(result_entry)

    # Save updated results
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)

    # ✅ Sort: high satisfaction, then fewer bugs, then fewer technical debt
    results.sort(
        key=lambda r: (-r["satisfaction"], r["bugs"], r["technical_debt"])
    )
 
    return render_template('end_game.html', team=team, results=results, last_id = result_entry["team_id"])   


####### helper functions #######
# This function generates a message based on whether expectations were met
def sprint_message_text(met_expectation, too_much_debt):
    if met_expectation:
        message = "✅ Expectations met! Satisfaction +1, Resources +1!"
    else:
        message = "❌ Expectations not met! Satisfaction -1!"
    if too_much_debt:
        message += "<br>❌ Technical debt more then 3! Capacity -1!"
    return message
    

def round_message_text(too_many_bugs):
    if too_many_bugs:
        return "❌ More then 3 bugs! Satisfaction -1!"

def round_message_text_old(met_expectation, too_many_bugs):
    if met_expectation and not too_many_bugs:
        return "✅ Expectations met! Satisfaction +1!"
    elif not met_expectation and too_many_bugs:
        return "❌ Expectations not met! Satisfaction -1!<br>❌ More then 3 bugs! Satisfaction -1!"
    elif met_expectation and too_many_bugs:
        return "✅ Expectations met! Satisfaction +1!<br>❌ More then 3 bugs! Satisfaction -1!"
    else:
        return "❌ Expectations not met! Satisfaction -1!"

def save_to_json(team, filename):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_FILE = os.path.join(BASE_DIR, filename)

    # Load existing results
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            results = json.load(f)
    else:
        results = []

    # Save current team result
    result_entry = {
        "team": team.name,
        "n_developers": len(team.developers),
        "satisfaction": team.satisfaction,
        "features": team.total_features,
        "optimizations": team.total_optimizations,
        "bugs": team.bugs,
        "technical_debt": team.technical_debt,
        "resources": team.resources,
        "team_id": session["team_id"]  # Unique ID for the result
    }

    # Append new result
    results.append(result_entry)

    # Save updated results
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)


if __name__ == '__main__':
    app.run(debug = True)
