# Presenter: Polls

The project showcases a demo app, Polls, with 5 security vulnerabilities and documentation on how to fix them: A CSRF vulnerability and four other flaws from the OSWAP Top Ten 2017 list.

LINK: https://github.com/jkuusto/presenter

## Table of Contents
- [Setup](#setup)
- [Flaws](#flaws)


## Setup

The project was made using Python version 3.12.0 and is likely compatible with older versions. It makes use of SQLite that is shipped with Python. The project requires Django 4.2.8, which can be installed globally or within a virtual environment using pip:
```
pip install Django==4.2.8
```
Newer versions of Django should work as well. There are no further dependencies, so a `requirements.txt` file is not included. However, you might consider installing `django-axes` to fix the brute force vulnerability in Flaw 4.

To run the project locally, clone the repository:
```
git clone https://github.com/jkuusto/presenter.git
cd presenter
```
The included db.sqlite3 has some preset data. You can use it as is. Alternatively, to start fresh, delete the database file and apply migrations:
```
python manage.py migrate
```
(Optional) If you migrated the database and need admin access, create a superuser:
```
python manage.py createsuperuser
```
Start the server:
```
python manage.py runserver
```
Finally, open your web browser and navigate to:
- `http://127.0.0.1:8000/polls/` or 
- `http://localhost:8000/polls/`


## Flaws

### FLAW 1: Cross-Site Request Forgery (CSRF)
#### Exact Source Link Pinpointing Flaw 1
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L51
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L9
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L36
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/index.html#L26

#### Description of Flaw 1
Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on the application where they are logged in. This is possible because the app does not verify the request's origin.
- The victim is logged into the polling application and has a valid session with the site.
- The victim is tricked into visiting a malicious site created by the attacker.
- The malicious site contains a form that auto-submits a request to the polling application, using the victim's authenticated session.
The polling application processes the request as if it were initiated by the victim. The threat actor can manipulate the results of a poll by casting votes without the users' knowledge or they could introduce inappropriate or misleading choices to an existing poll question.

Example: The threat actor has tricked the victim to click a link to a site and the victim's authentication is abused to vote for choice 1 automatically: 
```
<form action="http://localhost:8000/polls/1/vote/" method="post" id="snkeakyVoteForm">
    <input type="hidden" name="choice" value="1">
    <input type="submit" value="Submit Vote">
</form>

<script>
    document.getElementById('sneakyVoteForm').submit();
</script>
```
#### How to Fix It
Add `'django.middleware.csrf.CsrfViewMiddleware'` in settings.py and add `{% csrf_token %}` to the Vote, Add New Choice, and Add New Poll forms in the detail.html and index.html documents (see the source links above). This will make sure that the forms send a CSRF token to the server protecting users from actions performed without their consent.

It is also good practice to add a CSRF token even to forms that do not require authentication, such as the Add a Comment, Login, and Register forms: 
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L57
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/auth.html#L13
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/auth.html#L22

<br>

### FLAW 2: Injection
#### Exact Source Link Pinpointing Flaw 2
- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L67
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L37

#### Description of Flaw 2
A threat actor can exploit unsanitized SQL handling to inject SQL statements via user forms. In other words, this vulnerability allows the attacker to execute arbitrary SQL commands by manipulating input data.

Example: The threat actor types SQL values in the Add New Choice form on a poll detail page to create a choice while setting an arbitrary vote count. The following injection payload would create a choice "A thousand votes" and set its vote count to 1000:
```
A thousand votes', 1000); --
```
#### How to Fix It
1. Use Django's ORM for Database Operations.<br>
Modify the post method in views.py to use Django's ORM (Object-Relational Mapping), which automatically escapes input data to prevent SQL injection:
```
# views.py
def post(self, request, *args, **kwargs):
    form = ChoiceForm(request.POST)
    if form.is_valid():
        choice = form.save(commit=False)
        choice.question = self.get_object()
        choice.save()
        return redirect('polls:detail', pk=self.get_object().pk)
    return render(request, self.template_name, {'form': form, 'question': self.get_object()})
```
- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L70
2. Use Django Forms for input Handling.<br>
In detail.html, instead of the default html form, use `{{ form.as_p }}` to enable Django's form rendering which provides built-in protection against SQL injection.
```
<!-- detail.html -->
<form method="post">
    {{ form.as_p }}
    <button type="submit">Add choice</button>
</form>
```
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L39

<br>

### FLAW 3: Cross-Site Scripting (XSS)
#### Exact Source Link Pinpointing Flaw 3
- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L158
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L49

#### Description of Flaw 3
Cross-Site Scripting (XSS) allows a threat actor to inject malicious scripts into the webpages viewed by other users. The comments section of the poll detail page does not properly escape user input when processed and stored by the backend. This user input is then rendered with the |safe filter on the frontend, allowing the execution of arbitrary HTML or JavaScript code and leading to the execution of injected scripts.

Example 1: Entering the following script as a comment, misguides users to vote for the wrong choice: 
```
<script>alert('Admin notice: There is an error in the poll, choices 1 and 2 have been swapped. Vote 1 for choice 2, and vote 2 for choice 1');</script>
```
Example 2: Instead of rendering the page normally, render only a h1 header claiming that the poll has been closed, which also prevents the user from voting as the forms are not rendered:
```
<script>document.body.innerHTML = '<h1>This Poll has been closed.</h1>';</script>
```
#### How to Fix It
1. Escape characters when adding comments. <br>
Add `comment.comment_text = escape(comment.comment_text)` to the add_comment function. This ensures that the user content is escaped properly when stored in the database however it may be rendered later.

- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L157
2. Escape characters when rendering comments. <br>
Remove the `|safe` filter when rendering comments. This enables Django's built-in backend mechanisms to ensure that user-generated content is properly escaped when rendered:
```
<!-- detail.html -->
<ul>
    {% for comment in question.comment_set.all %}
        <li>{{ comment.comment_text }}</li>
    {% endfor %}
</ul>
```
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L51

<br>

### FLAW 4: Broken Authentication
#### Exact Source Link Pinpointing Flaw 4
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L91
#### Description of Flaw 4
Main flaw: There are no requirements for password creation, allowing weak passwords to be set by users. A user could set their password even as just "1" during registration on the auth page, which is very easy to guess or discover by brute force.

Another interesting issue is that by default Django apps do not lock out users from trying to brute force login credentials. That is also the case in this app.
#### How to Fix It
To fix the weak password policy, use the validators.py file with a custom password validator that requires passwords to include at least one lower case letter, one upper case letter, one digit, and one symbol.
- https://github.com/jkuusto/presenter/blob/main/polls/validators.py#L1

Then set password requirements for password creation in settings.py (see source link from before).

The three other settings assert these additional requirements for passwords:
- Prevent passwords that are similiar to the username or email address
- Set a minimum length for passwords (14 in this case)
- Prevent using the most common passwords that are easy to guess

As an additional measure, the easiest way to fix the brute force vulnerability is to use a third party solution, like `django-axes`.
```
pip install django-axes
```
After installation, `django-axes` is configured in settings.py:
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L41
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L52
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L108

Finally, run `python manage.py migrate`.

<br>

### FLAW 5: Broken Access Control
#### Exact Source Link Pinpointing Flaw 5
- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L77
#### Description of Flaw 5
The design of the app dictates that only logged-in users can vote and view the vote results. After an authenticated user has voted, they are automatically redirected to the poll question's results page. There is no direct navigational link to view the results without voting.

However, due to a Broken Access Control vulnerability, specifically an Insecure Direct Object References (IDOR) flaw, an anonymous user can access the results page by manipulating the URL directly in the browser's address bar. For example, to access the results of poll question id 1, one could go directly to `/polls/1/results/`. This way, the link can also be shared on a public forum exposing poll data that is meant to be seen only by authorized users.
#### How to Fix It
Add a `@method_decorator(login_required, name='dispatch')` decorator to the ResultsView class in views.py (see source code link above). This ensures that access to each results view is granted only when a user is logged in, fixing the broken access control flaw.

