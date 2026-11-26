from flask import Flask, render_template, session, redirect, url_for, flash
from forms.auth_forms import RegistrationForm, LoginForm
from forms.subscriptions_forms import AddSubscription, EditSubscription, DeleteSubscription
from config.settings import SECRET_KEY
from db.queries import user_exists, save_user, get_user_by_username, get_user_by_id, save_subscription, get_subscriptions, get_subscription_by_id, update_subscription, delete_subscription
from security.hashing import hash_password, check_password
from security.decorators import login_required
from services.billing import calculate_next_payment, total_price
from security.tokens import generate_subscription_id
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from security.decorators import demo_session_required
from security.limiter import limiter

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

limiter.init_app(app)

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB


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
@limiter.limit("5 per minute")
@limiter.limit("100 per 7 days")
@limiter.limit("1000 per month")
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

    form.username.data = ''
    form.password.data = ''

    return render_template('registration.html', form=form)


@app.get('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)


@app.post('/login')
@limiter.limit("5 per minute")
@limiter.limit("100 per 7 days")
@limiter.limit("1000 per month")
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

        form.username.data = ''
        form.password.data = ''

        return render_template('login.html', form=form, message='Username or password incorrect.')

    form.username.data = ''
    form.password.data = ''

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
    form = DeleteSubscription()

    if not form.validate_on_submit():
        flash('Invalid request.', 'error')
        return redirect(url_for('my_subscriptions'))

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


@app.get('/demo')
def demo():
    return render_template('demo.html')


@app.get('/demo_all_subscriptions')
@demo_session_required
def demo_all_subscriptions():
    return render_template('demo_all_subscriptions.html', total=session['demo_total'], all_subscriptions=session['demo_all_subscriptions'])


@app.get('/demo_add')
@demo_session_required
def demo_add():
    form = AddSubscription()
    return render_template('demo_add_subscription.html', form=form)


@app.post('/demo_add')
@demo_session_required
def demo_add_post():
    form = AddSubscription()

    if form.validate_on_submit():
        all_subscriptions = session['demo_all_subscriptions']

        if len(all_subscriptions) >= 3:
            flash('You cannot add more than three subscriptions.', "error")
            return redirect(url_for('demo_all_subscriptions'))

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

        next_date = calculate_next_payment(duration, started_on, billing_cycle)

        data = {
            'subscription_id': generate_subscription_id(),
            'service': service,
            'started_on': started_on.strftime('%d.%m.%Y'),
            'next_payment': next_date.strftime('%d.%m.%Y'),
            'duration': duration,
            'plan': plan,
            'notes': notes,
            'price': float(price),
            'category': category,
            'currency': currency,
            'billing_cycle': billing_cycle,
            'auto_renew': auto_renew,
            'created_at': started_on.strftime('%d.%m.%Y'),
            'updated_at': started_on.strftime('%d.%m.%Y')
        }


        all_subscriptions.append(data)

        session['demo_all_subscriptions'] = all_subscriptions
        session['demo_total'] = total_price(all_subscriptions)

        flash('Subscription added successfully.', "success")
        return redirect(url_for('demo_all_subscriptions'))

    flash('Unable to save subscription. Please try again.', 'error')
    return redirect(url_for('demo_add'))


@app.get('/demo_edit_note/<subscription_id>')
@demo_session_required
def demo_edit_note(subscription_id):
    form = EditSubscription()
    for sub in session['demo_all_subscriptions']:
        if sub['subscription_id'] == subscription_id:
            form.notes.data = sub['notes']
            return render_template('demo_edit_note.html', form=form, subscription_id=subscription_id, service=sub['service'])

    flash("Subscription doesn't exist.", 'error')
    return redirect(url_for('demo_all_subscriptions'))


@app.post('/demo_edit_note/<subscription_id>')
@demo_session_required
def demo_edit_note_post(subscription_id):
    form = EditSubscription()
    if form.validate_on_submit():

        all_subscriptions = session['demo_all_subscriptions']

        for sub in all_subscriptions:
            if sub['subscription_id'] == subscription_id:
                sub['notes'] = form.notes.data

                session['demo_all_subscriptions'] = all_subscriptions

                flash('Note updated successfully.', 'success')
                return redirect(url_for('demo_all_subscriptions'))

        flash("Subscription doesn't exists.", 'error')
        return redirect(url_for('demo_all_subscriptions'))

    flash('Something went wrong. Try again!', 'error')
    return redirect(url_for('demo_all_subscriptions'))


@app.get('/demo_edit_subscription/<subscription_id>')
@demo_session_required
def demo_edit_subscription(subscription_id):
    form = AddSubscription()
    all_subscriptions = session['demo_all_subscriptions']

    for sub in all_subscriptions:
        if sub['subscription_id'] == subscription_id:
            form.service.data = sub['service']
            form.price.data = sub['price']
            form.currency.data = sub['currency']
            form.category.data = sub['category']
            form.billing_cycle.data = sub['billing_cycle']
            form.duration.data = sub['duration']
            form.started_on.data = datetime.strptime(sub['started_on'],'%d.%m.%Y').date()
            form.plan.data = sub['plan']
            form.notes.data = sub['notes']
            form.auto_renew.data = sub['auto_renew']

            return render_template('demo_edit_subscription.html', form=form, subscription_id=subscription_id)

    flash("Subscription doesn't exist", 'error')
    return redirect(url_for('my_subscriptions'))


@app.post('/demo_edit_subscription_post/<subscription_id>')
@demo_session_required
def demo_edit_subscription_post(subscription_id):
    form = AddSubscription()
    all_subscriptions = session['demo_all_subscriptions']

    if form.validate_on_submit():
        for sub in all_subscriptions:
            if sub['subscription_id'] == subscription_id:
                sub['service'] = form.service.data
                sub['price'] = form.price.data
                sub['currency'] = form.currency.data
                sub['category'] = form.category.data
                sub['billing_cycle'] = form.billing_cycle.data
                sub['duration'] = form.duration.data
                sub['started_on'] = form.started_on.data.strftime('%d.%m.%Y')
                sub['next_payment'] = calculate_next_payment(
                    form.duration.data, form.started_on.data, form.billing_cycle.data
                ).strftime('%d.%m.%Y')
                sub['plan'] = form.plan.data
                sub['notes'] = form.notes.data
                sub['auto_renew'] = form.auto_renew.data

                session['demo_all_subscriptions'] = all_subscriptions
                session['demo_total'] = total_price(all_subscriptions)

                flash('Subscription updated successfully.', 'success')
                return redirect(url_for('demo_all_subscriptions'))

        flash("Subscription doesn't exist.", 'error')
        return redirect(url_for('demo_all_subscriptions'))

    flash('Something went wrong. Try again!', 'error')
    return redirect(url_for('demo_edit_subscription', subscription_id=subscription_id))


@app.get('/demo_delete_subscription/<subscription_id>')
@demo_session_required
def demo_delete_subscription(subscription_id):
    form = DeleteSubscription()
    all_subscriptions = session['demo_all_subscriptions']

    for sub in all_subscriptions:
        if sub['subscription_id'] == subscription_id:

            return render_template(
                'demo_delete_subscription.html',
                subscription_id=subscription_id,
                form=form,
                service=sub['service'],
                price=sub['price'],
                currency=sub['currency'],
                category=sub['category'],
                billing_cycle=sub['billing_cycle']
            )

    flash("Subscription doesn't exist", 'error')
    return redirect(url_for('demo_all_subscriptions'))


@app.post('/demo_delete_subscription_post/<subscription_id>')
@demo_session_required
def demo_delete_subscription_post(subscription_id):
    form = DeleteSubscription()

    if not form.validate_on_submit():
        flash('Invalid request.', 'error')
        return redirect(url_for('demo_all_subscriptions'))

    all_subscriptions = session['demo_all_subscriptions']
    remain_subscriptions = []


    for sub in all_subscriptions:
        if sub['subscription_id'] != subscription_id:
            remain_subscriptions.append(sub)

    if len(remain_subscriptions) == len(all_subscriptions):
        flash("Subscription doesn't exist.", 'error')
        return redirect(url_for('demo_all_subscriptions'))


    session['demo_all_subscriptions'] = remain_subscriptions
    session['demo_total'] = total_price(remain_subscriptions)

    flash('Subscription deleted.', 'success')
    return redirect(url_for('demo_all_subscriptions'))


if __name__ == '__main__':
    app.run(debug=False)