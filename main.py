from flask import Flask, redirect, url_for, render_template, request, session
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
        rounds = int(request.form['total_rounds'])
        session['team_name'] = team_name
        session['total_rounds'] = rounds
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
        team = Team.from_dict(session['team_data'])
        # Load previous game state to get sprints_per_round
        prev_game_data = session['game_data']
        sprints_per_round = prev_game_data['sprints_per_round'] 
        # Generate new expectation if it's the start of a new round
        expectation = None if (sprint_num + 1) % sprints_per_round == 1 else prev_game_data.get('expectation')
        game = Game(team, expectation=expectation, total_sprints=prev_game_data['total_sprints'])

    else:
        # Before the very 1st sprint, initialize team and game
        team = Team(team_name)
        game = Game(team)
        game.total_sprints = session['total_rounds'] * game.sprints_per_round
        # Save initial game state in session
        session['game_data'] = game.to_dict()
        # Update team state in session
        session['team_data'] = team.to_dict()

    round_num  = sprint_num // game.sprints_per_round + 1
    sprint_in_round = sprint_num % game.sprints_per_round + 1
    error = None
    # Get round message from session if it exists
    round_message = session.pop('round_message', None)

    if request.method == 'POST':
        try:
            allocations = {
                'New feature': int(request.form.get('feature', 0)),
                'Optimization':  int(request.form.get('optimization')),
                'Testing':  int(request.form.get('testing', 0)),
                'Bug resolution':  int(request.form.get('bugfix', 0)),
                'Technical debt':  int(request.form.get('technical_debt', 0))
            }
            game.play_sprint(sprint_num, allocations = allocations)

            # Update team state in session
            session['team_data'] = team.to_dict()

            ##### Sprint/Round/Game end logic ####
            if (sprint_num + 1) >= game.total_sprints:
                game.end_round()
                game.end_game()
                # Update team state in session
                session['team_data'] = team.to_dict()
                return redirect(url_for('end_game'))
            
            elif (sprint_num + 1) % game.sprints_per_round == 0:
                met_expectations = game.end_round()
                round_message = round_message_text(met_expectations)
                session['round_message'] = round_message
                # Update team state in session
                session['team_data'] = team.to_dict()
                return redirect(url_for('play_sprint', sprint_num = sprint_num + 1))
            
            else:
                return redirect(url_for('play_sprint', sprint_num = sprint_num + 1))
            
        except ValueError as e:
            error = str(e)    

    return render_template(
        'play_sprint.html', game=game, sprints_per_round=game.sprints_per_round,
        sprint_in_round=sprint_in_round, round_num=round_num, rounds=session['total_rounds'],
        team=team, error=error, round_message=round_message
    )

@app.route('/end_game')
def end_game():
    team_name = session.get('team_name')
    if not team_name:
        return redirect(url_for('start_game'))
    
    team = Team.from_dict(session['team_data'])

    return render_template('end_game.html', team=team)   


####### helper functions #######
# This function generates a message based on whether expectations were met
def round_message_text(met_expectation):
    if met_expectation:
        return "✅ Expectations met! Satisfaction +1!"
    else:
        return "❌ Expectations not met! Satisfaction -1!"


if __name__ == '__main__':
    app.run(debug = True)
# This code sets up a basic Flask web application that returns "Hello, World!" when accessed