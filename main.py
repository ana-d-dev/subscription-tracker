from flask import Flask, render_template, session, redirect, url_for, flash
from forms.auth_forms import RegistrationForm, LoginForm
from forms.subscriptions_forms import AddSubscription, EditSubscription, DeleteSubscription
from config.settings import SECRET_KEY
from db.queries import user_exists, save_user, get_user_by_username, get_user_by_id, save_subscription, get_subscriptions, get_subscription_by_id, update_subscription, delete_subscription
from security.hashing import hash_password, check_password
from security.decorators import login_required
from services.billing import calculate_next_payment, total_price


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@app.context_processor
def inject():
    return {'logged_in': 'user_id' in session}


@app.route('/')
def home():
    return render_template('home.html')


@app.get('/registration')
def registration():
    form = RegistrationForm()
    return render_template('registration.html', form=form)



@app.post('/registration')
def registration_post():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if not user_exists(username):
            hashed_password = hash_password(password)
            data = {'username': username, 'hashed_password': hashed_password}
            save_user(data)
            user = get_user_by_username(username)
            session['user_id'] = user['id']

            flash(f'Registration successful. Welcome {username}!', 'success')

            return redirect(url_for('profile'))

        return render_template('registration.html', form=form, message='Username is taken')

    return render_template('registration.html', form=form)


@app.get('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.post('/login')
def login_post():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if check_password(username, password):
            user = get_user_by_username(username)
            session['user_id'] = user['id']

            flash(f'You are successfully logged in. Hello {username}!', 'success')

            return redirect(url_for('profile'))

        return render_template('login.html', form=form, message='Username or password incorrect.')

    return render_template('login.html', form=form)



@app.get('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    number_of_subscriptions = len(get_subscriptions(session['user_id']))

    if not user:
        flash('User does not exist.', 'error')
        session.clear()
        return redirect(url_for('login'))

    return render_template('profile.html', user=user, number_of_subscriptions=number_of_subscriptions)



@app.get('/add_subscriptions')
@login_required
def add_subscription():
    form = AddSubscription()
    return render_template('add_subscription.html', form=form)



@app.post('/add_subscriptions')
@login_required
def add_subscription_post():
    form = AddSubscription()

    if form.validate_on_submit():
        service = form.service.data
        started_on = form.started_on.data
        duration = form.duration.data
        price = form.price.data
        category = form.category.data
        currency = form.currency.data
        plan = form.plan.data
        billing_cycle = form.billing_cycle.data
        auto_renew = form.auto_renew.data
        notes = form.notes.data
        user_id = session['user_id']

        next_date = calculate_next_payment(duration, started_on, billing_cycle)

        data = {
            'user_id': user_id,
            'service': service,
            'started_on': started_on,
            'next_payment': next_date,
            'duration': duration,
            'plan': plan,
            'notes': notes,
            'price': price,
            'category': category,
            'currency': currency,
            'billing_cycle': billing_cycle,
            'auto_renew': auto_renew
        }

        save_subscription(data)

        flash('Subscription added successfully.', "success")

        return redirect(url_for('my_subscriptions'))

    flash('Unable to save subscription. Please try again.', 'error')

    return redirect(url_for('add_subscription'))


@app.get('/my_subscriptions')
@login_required
def my_subscriptions():
    user_id = session['user_id']
    all_subscriptions = get_subscriptions(user_id)
    total = total_price(all_subscriptions)

    return render_template('my_subscriptions.html', all_subscriptions=all_subscriptions, total=total)



@app.get('/subscription_details/<int:subscription_id>')
@login_required
def subscription_details(subscription_id):
    user_id = session['user_id']
    subscription_detail = get_subscription_by_id(subscription_id, user_id)

    if subscription_detail:
        return render_template('notes.html', subscription_detail=subscription_detail)

    flash("Subscription doesn't exist", 'error')

    return redirect(url_for('my_subscriptions'))


@app.get('/edit/<int:subscription_id>')
@login_required
def edit_subscription(subscription_id):
    form = AddSubscription()
    user_id = session['user_id']

    subscription_detail = get_subscription_by_id(subscription_id, user_id)

    if subscription_detail:
        form.service.data = subscription_detail['service']
        form.price.data = subscription_detail['price']
        form.currency.data = subscription_detail['currency']
        form.category.data = subscription_detail['category']
        form.billing_cycle.data = subscription_detail['billing_cycle']
        form.duration.data = subscription_detail['duration']
        form.started_on.data = subscription_detail['started_on']
        form.plan.data = subscription_detail['plan']
        form.notes.data = subscription_detail['notes']
        form.auto_renew.data = subscription_detail['auto_renew']

        return render_template('edit_subscription.html', form=form, subscription_detail=subscription_detail)

    flash("Subscription doesn't exist", 'error')

    return redirect(url_for('my_subscriptions'))


@app.post('/edit/<int:subscription_id>')
@login_required
def edit_subscription_post(subscription_id):
    form = AddSubscription()

    if form.validate_on_submit():
        service = form.service.data
        started_on = form.started_on.data
        duration = form.duration.data
        price = form.price.data
        category = form.category.data
        currency = form.currency.data
        billing_cycle = form.billing_cycle.data
        auto_renew = form.auto_renew.data
        notes = form.notes.data
        plan = form.plan.data
        user_id = session['user_id']

        next_date = calculate_next_payment(duration, started_on, billing_cycle)

        data = {
            'user_id': user_id,
            'service': service,
            'started_on': started_on,
            'next_payment': next_date,
            'plan': plan,
            'duration': duration,
            'notes': notes,
            'price': price,
            'category': category,
            'currency': currency,
            'billing_cycle': billing_cycle,
            'auto_renew': auto_renew
        }

        update_subscription(subscription_id, user_id, data)

        flash('Subscription updated successfully.', 'success')

        return redirect(url_for('my_subscriptions'))

    flash('Unable to update subscription. Please try again.', 'error')

    subscription_detail = get_subscription_by_id(subscription_id, session['user_id'])

    if subscription_detail:
        return render_template('edit_subscription.html', form=form, subscription_detail=subscription_detail)

    return redirect(url_for('my_subscriptions'))



@app.get('/edit_note/<int:subscription_id>')
@login_required
def edit_note(subscription_id):
    form = EditSubscription()
    user_id = session['user_id']
    subscription_detail = get_subscription_by_id(subscription_id, user_id)


    if subscription_detail:
        form.notes.data = subscription_detail['notes']

        return render_template('edit_note.html', form=form, subscription_detail=subscription_detail)

    flash("Subscription doesn't exist", 'error')

    return redirect(url_for('my_subscriptions'))



@app.post('/edit_note/<int:subscription_id>')
@login_required
def edit_note_post(subscription_id):
    form =  EditSubscription()
    if form.validate_on_submit():
        user_id = session['user_id']
        note = form.notes.data
        data = {'notes': note}
        update_subscription(subscription_id, user_id, data)

        flash('Note updated successfully.', 'success')

        return redirect(url_for('subscription_details', subscription_id=subscription_id))

    flash('Unable to update note.', 'error')

    return redirect(url_for('my_subscriptions'))



@app.get('/delete/<int:subscription_id>')
@login_required
def remove_subscription(subscription_id):
    form = DeleteSubscription()
    user_id = session['user_id']

    subscription_detail = get_subscription_by_id(subscription_id, user_id)

    if subscription_detail:
        form.service.data = subscription_detail['service']
        form.price.data = subscription_detail['price']
        form.category.data = subscription_detail['category']

        return render_template('delete_subscription.html', form=form, subscription_detail=subscription_detail)

    flash('Unable to delete note.', 'error')

    return redirect(url_for('my_subscriptions'))



@app.post('/delete/<int:subscription_id>')
@login_required
def remove_subscription_post(subscription_id):
    user_id = session['user_id']
    subscription_detail = get_subscription_by_id(subscription_id, user_id)

    if not subscription_detail:
        flash("Subscription doesn't exist.", 'error')
        return redirect(url_for('my_subscriptions'))

    delete_subscription(subscription_id, user_id=user_id)
    flash('Subscription deleted successfully.', 'success')
    return redirect(url_for('my_subscriptions'))



@app.get('/logout')
@login_required
def logout():
    session.clear()
    flash('You successfully logged out.', 'success')
    return redirect(url_for('home'))


@app.get('/about')
def about():
    return render_template('about.html')


@app.get('/features')
def features():
    return render_template('features.html')


@app.get('/tech_stack')
def tech_stack():
    return render_template('tech_stack.html')


@app.get('/privacy')
def privacy():
    return render_template('privacy.html')


@app.get('/terms')
def terms():
    return render_template('terms.html')


@app.get('/contact')
def contact():
    return render_template('contact.html')

@app.get('/how_to_use')
def how_to_use():
    return render_template('how_to_use.html')


if __name__ == '__main__':
    app.run(debug=True)