from sre_constants import SUCCESS
from wc_prediction import app
from flask import render_template, redirect, url_for, flash, request
from wc_prediction.models import Teams, User
from wc_prediction import db
from wc_prediction.forms import RegisterForm, LoginForm, AdvanceTeamForm, PopAdvancedTeamForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/predictions', methods=['GET', 'POST'])
@login_required
def predict_group_stage():
    # ------ Bellow line of code need to be transferred as init to setup database :::: current problem insert current_user.id from init file or some /home setup page --------------
    # participating_teams = [
    #     {'group': 'A', 'qualified_teams': 'Qatar'},
    #     {'group': 'A', 'qualified_teams': 'Netherlands'},
    #     {'group': 'A', 'qualified_teams': 'Senegal'},
    #     {'group': 'A', 'qualified_teams': 'Ecuador'},
    #     {'group': 'B', 'qualified_teams': 'England'},
    #     {'group': 'B', 'qualified_teams': 'USA'},
    #     {'group': 'B', 'qualified_teams': 'Wales'},
    #     {'group': 'B', 'qualified_teams': 'Iran'},
    #     {'group': 'C', 'qualified_teams': 'Argentina'},
    #     {'group': 'C', 'qualified_teams': 'Mexico'},
    #     {'group': 'C', 'qualified_teams': 'Poland'},
    #     {'group': 'C', 'qualified_teams': 'Saudi Arabia'},
    #     {'group': 'D', 'qualified_teams': 'France'},
    #     {'group': 'D', 'qualified_teams': 'Denmark'},
    #     {'group': 'D', 'qualified_teams': 'Tunisia'},
    #     {'group': 'D', 'qualified_teams': 'Australia'},
    #     {'group': 'E', 'qualified_teams': 'Spain'},
    #     {'group': 'E', 'qualified_teams': 'Germany'},
    #     {'group': 'E', 'qualified_teams': 'Japan'},
    #     {'group': 'E', 'qualified_teams': 'Costa Rica'},
    #     {'group': 'F', 'qualified_teams': 'Belgium'},
    #     {'group': 'F', 'qualified_teams': 'Croatia'},
    #     {'group': 'F', 'qualified_teams': 'Morocco'},
    #     {'group': 'F', 'qualified_teams': 'Canada'},
    #     {'group': 'G', 'qualified_teams': 'Brazil'},
    #     {'group': 'G', 'qualified_teams': 'Switzerland'},
    #     {'group': 'G', 'qualified_teams': 'Serbia'},
    #     {'group': 'G', 'qualified_teams': 'Cameroon'},
    #     {'group': 'H', 'qualified_teams': 'Portugal'},
    #     {'group': 'H', 'qualified_teams': 'Uruguay'},
    #     {'group': 'H', 'qualified_teams': 'South Korea'},
    #     {'group': 'H', 'qualified_teams': 'Ghana'},
    # ]
    # sql_clear_table_request = "delete from Teams"
    # db.session.execute(sql_clear_table_request)
    # db.session.commit()
    # for primary_key, data_dict in enumerate(participating_teams):
    #     sql_request = "insert into Teams values ({}, '{}', '{}', {}, '{}')".format(primary_key, data_dict['group'], data_dict['qualified_teams'], current_user.id, 1)
    #     db.session.execute(sql_request)
    #     db.session.commit()
    selected_team_form = AdvanceTeamForm()
    not_selected_team_form = PopAdvancedTeamForm()
       
    if request.method == "POST":
        selected_team = request.form.get('selected_team') 
        s_team_obj = Teams.query.filter_by(qualified_teams = selected_team).first()
        #Advancing the team logic
        if s_team_obj: # quick check if s_team_obj is query.first() result
            s_team_obj.adding()  # seting flag to 2 (Advanced)
            flash(f"You selected {s_team_obj.qualified_teams} as team who will advance in group: {s_team_obj.group}!", category='success')
        db.session.commit()
        #Removing team from advanced teams logic
        not_adv = request.form.get('not_adv')
        not_adv_team_obj = Teams.query.filter_by(qualified_teams = not_adv).first()
        if not_adv_team_obj:
            not_adv_team_obj.changing()
            flash(f"You put {not_adv_team_obj.qualified_teams} back to list of teams with available selection")
        db.session.commit()
        return redirect(url_for('predict_group_stage'))
        
    if request.method == "GET":
        teams_to_pop = Teams.query.filter_by(advance_f = 2) # sending on the right side of the page all the objects of class Teams with advance_f (flag) to 2 (Advanced)
        print(teams_to_pop)
        advanced_teams = Teams.query.filter_by(advance_f = 1) # sending on the left side of the page all the objects of class Teams with advance_f (flag) to 1 (Not advanced)
        print(advanced_teams)
        return render_template('predictions.html', advanced_teams=advanced_teams, teams_to_pop=teams_to_pop, selected_team_form=selected_team_form, not_selected_team_form=not_selected_team_form)


@app.route('/register', methods = ['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                             email_address=form.email_address.data,
                             password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('predict_group_stage'))
    if form.errors != {}: #errors made by not following restrictions of validators in forms.py
        for err_msg in form.errors.values():
            flash(f'Some errors occured during creation of user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('predict_group_stage'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home_page'))