# presenter

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
Newer versions of Django should work as well. There are no further dependencies, so a `requirements.txt` file is not included.

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
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L50
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L9
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L36
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/index.html#L26

#### Description of Flaw 1
Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on the application where they are logged in. This is possible because the app does not verify the request's origin.
- The victim is logged into the polling application and has a valid session with the site.
- The victim is tricked into visiting a malicious site created by the attacker.
- The malicious site contains a form that auto-submits a request to the polling application, using the victim's authenticated session.
The polling application processes the request as if it were initiated by the victim. The threat actor may want to manipulate the results of a poll by casting votes without the users' knowledge or they may want to introduce inappropriate or misleading choices to an existing poll question.

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
Add `'django.middleware.csrf.CsrfViewMiddleware'` middleware in settings.py and add `{% csrf_token %}` to the Vote, Add New Choice, and Add New Poll forms in the detail.html and index.html documents (see the source links above). This will make sure that the forms include CSRF tokens protecting the users from unwanted actions performed without their consent.

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

Example: The threat actor types SQL values in the Add New Choice form on a poll detail page to create a choice while setting an arbitrary vote count. This injection payload would create a choice "A thousand votes" and set its vote count to 1000:
```
A thousand votes', 1000); --
```
#### How to Fix It
1. Use Django's ORM for Database Operations.
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
2. Use Django Forms for input Handling.
In detail.html, instead of the default html form, use `{{ form.as_p }}` to make use of Django's form rendering which provides built-in protection against SQL injection.
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
- https://github.com/jkuusto/presenter/blob/main/polls/templates/polls/detail.html#L49

#### Description of Flaw 3
Cross-Site Scripting (XSS) allows a threat actor to inject malicious scripts into the webpages viewed by other users. The comments section of the poll detail page does not properly escape user input as they are rendered with the safe filter allowing execution of arbitrary HTML or JavaScript code leading to execution of injected script.

Example 1: Entering the following script as a comment, misguides users to vote for the wrong choice: 
```
<script>alert('Admin notice: There is an error in the poll, choices 1 and 2 have been swapped. Vote 1 for choice 2, and vote 2 for choice 1');</script>
```
Example 2: Instead of rendering the page normally, render only a h1 header claiming that the poll has been closed, which also prevents the user from voting as the forms are not rendered:
```
<script>document.body.innerHTML = '<h1>This Poll has been closed.</h1>';</script>
```
#### How to Fix It
Remove the ```|safe``` filter when rendering comments ensuring that the user-generated content is properly escaped:
```
<!-- detail.html -->
<ul>
    {% for comment in question.comment_set.all %}
        <li>{{ comment.comment_text }}</li>
    {% endfor %}
</ul>
```

<br>

### FLAW 4: Broken Authentication
#### Exact Source Link Pinpointing Flaw 4
- https://github.com/jkuusto/presenter/blob/main/presenter/settings.py#L89
#### Description of Flaw 4
There are no requirements for password creation, allowing weak passwords to be set by users. A user could set their password even as just "1" during registration.

Another issue is that the app does not lock out users trying to brute force login credentials. For example, a threat actor can use a dictionary attack to try to login as another user.
#### How to Fix It
To fix the weak password policy, create a validators.py file in the app with the following custom password validator:
```
# validators.py
import re
from django.core.exceptions import ValidationError

class CharacterPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError("Must include lowercase letter")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Must include uppercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Must include digit")
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise ValidationError("Must include symbol")

    def get_help_text(self):
        return "Password must include lowercase letter, uppercase letter, digit, and symbol"
```
Then set password requirements for password creation in settings.py
```
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 
        'OPTIONS': {
            'min_length': 14, 
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'polls.validators.CharacterPasswordValidator',
    },
]
```
These settings assert four requirements for passwords:
- Prevents passwords that are similiar to the username or email address
- Sets a minimum length for passwords (14 in this case)
- Prevents using the most common passwords that are easy to guess
- Requires passwords to include at least one lower case letter, one upper case letter, one digit, and one symbol

To fix the brute force vulnerability, the easiest way is to use a third party solution, like `django-axes`. After installation, `django-axes` is configured in settings.py:
```
# settings.py
INSTALLED_APPS = [
    'axes',
]
MIDDLEWARE = [
    'axes.middleware.AxesMiddleware',
]
AXES_FAILURE_LIMIT = 3 
AXES_COOLOFF_TIME = 1
```` 
Finally, run `python manage.py migrate`.

<br>

### FLAW 5: Broken Access Control
#### Exact Source Link Pinpointing Flaw 5
- https://github.com/jkuusto/presenter/blob/main/polls/views.py#L72
#### Description of Flaw 5
It is the intent of the app that only logged-in users can vote and view the vote results. Only an authenticated user can vote, after which they are automatically redirected to the poll question's results page. There is no direct navigational link to view the results without voting.

However, due to a Broken Access Control vulnerability, specifically an Insecure Direct Object References (IDOR) flaw, an anonymous user can access the results page by typing the page URL directly into the browser's address bar. For example, to access the results of poll question id 1, one could go directly to ```/polls/1/results/```. This way, the link can also be shared on a public forum exposing poll data that is meant to be seen only by authorized users.
#### How to Fix It
Add a ```@method_decorator(login_required, name='dispatch')``` decorator to the ResultsView class:
```
# views.py
@method_decorator(login_required, name='dispatch')
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
```
This enforces that access to each results view is granted only when a user is logged in, fixing the broken access control flaw.

