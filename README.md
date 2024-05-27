# presenter

This project showcases a demo app, Polls, with 5 security vulnerabilities and documentation on how to fix them: A CSRF vulnerability and four other flaws from the OSWAP Top Ten 2017 list.


## Table of Contents
- [Setup](#setup)
- [Flaws](#flaws)


## Setup

Coming soon.


## Flaws

### FLAW 1: Cross-Site Request Forgery (CSRF)
#### Exact Source Link Pinpointing Flaw 1
- index.html | <!-- {% csrf_token %} -->
- detail.html | <!-- {% csrf_token %} -->
- auth.html | <!-- {% csrf_token %} -->
- settings.py | # 'django.middleware.csrf.CsrfViewMiddleware',

#### Description of Flaw 1
Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on the application where they are logged in. This is because the app does not verify the request's origin.
- The victim is logged into the polling application and has a valid session with the site.
- The victim is tricked into visiting a malicious site created by the attacker.
- The malicious site contains a form that auto-submits a request to the polling application, using the victim's authenticated session.
The polling application processes the request as if it were initiated by the victim. The threat actor may want to manipulate the results of a poll by casting votes without the users' knowledge or they may want to introduce inappropriate or misleading choices to an existing poll question.

Here is an example where the threat actor has tricked the victim to click a link to a site where the victim's authentication is abused to vote for choice 1 automatically: 
```
<form action="http://localhost:8000/polls/1/vote/" method="post" id="snkeakyForm">
    <input type="hidden" name="choice" value="1">
    <input type="submit" value="Submit Vote">
</form>

<script>
    document.getElementById('sneakyForm').submit();
</script>
```
#### How to Fix It
Add ```'django.middleware.csrf.CsrfViewMiddleware'``` middleware in settings.py and add ```{% csrf_token %}``` to all forms in the html documents. This will make sure that all forms include CSRF tokens protecting the users from unwanted actions performed without their consent.

<br>

### FLAW 2: Injection
#### Exact Source Link Pinpointing Flaw 2
- views.py | class DetailView | def post
- detail.html | second form

#### Description of Flaw 2
A threat actor can exploit unsanitized SQL handling to inject SQL statements via user forms. In other words, this vulnerability allows the attacker to execute arbitrary SQL commands by manipulating input data.

Example: The threat actor uses the choice creator form to make a new choice while setting an arbitrary vote tally. This injection payload would create a choice "A thousand votes" and set its vote tally to 1000:
```
A thousand votes', 1000); --
```
#### How to Fix It
1. Use Django's ORM for Database Operations.
- Modify the post method in views.py to use Django's ORM (Object-Relational Mapping), which automatically escapes input data to prevent SQL injection:
```
def post(self, request, *args, **kwargs):
    form = ChoiceForm(request.POST)
    if form.is_valid():
        choice = form.save(commit=False)
        choice.question = self.get_object()
        choice.save()
        return redirect('polls:detail', pk=self.get_object().pk)
    return render(request, self.template_name, {'form': form, 'question': self.get_object()})
```
2. Use Django Forms for input Handling.
- In detail.html, instead of the default html form, use ```{{ form.as_p }}``` to make use of Django's form rendering which provides built-in protection against SQL injection.

<br>

### FLAW 3: Cross-Site Scripting (XSS)
#### Exact Source Link Pinpointing Flaw 3
- detail.html | {{ comment.comment_text|safe }}

#### Description of Flaw 3
Cross-Site Scripting (XSS) allows a threat actor to inject malicious scripts into the webpages viewed by other users. The comments section of the poll detail page does not properly escape user input as they are rendered with the safe filter allowing execution of arbitrary HTML or JavaScript code leading to execution of injected script.

Example 1: Entering the following script to the comments, misguides users to vote for the wrong choice: 
```
<script>alert('Admin notice: There is an error in the poll, choices 1 and 2 have been swapped. Vote 1 for choice 2, and vote 2 for choice 1');</script>
```
Example 2: Instead of rendering the page normally, render only a h1 header claiming that the poll has been closed, which also prevents the user from voting because the forms are not rendered:
```
<script>document.body.innerHTML = '<h1>This Poll has been closed.</h1>';</script>
```
#### How to Fix It
Remove the ```|safe``` filter when rendering comments ensuring that the user-generated content is properly escaped.

<br>

### FLAW 4: Broken Authentication
#### Exact Source Link Pinpointing Flaw 4
- settings.py | AUTH_PASSWORD_VALIDATORS
#### Description of Flaw 4
There are no requirements for password creation, allowing weak passwords to be set by users. For example, a user could set their password as "1".

Another issue is that the app does not lock out users trying to brute force login credentials. A threat actor can try to login with a dictionary attack, for example.
#### How to Fix It
To fix the weak password policy, create a validators.py file in the app with the following custom password validator:
```
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

To fix the brute force vulnerability, the easiest way is to use a third party solution, like `django-axes`. After installing, `django-axes` is configured in settings.py:
```
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
- views.py | class ResultsView
#### Description of Flaw 5
It is the intent of the app that only logged-in users can vote and view the vote results. When an authenticated user votes, they are automatically redirected to the poll question's results page. There is no direct navigational link to the results.

However, due to a Broken Access Control vulnerability, in this case an Insecure Direct Object References (IDOR) flaw, an anonymous user can access the results page by typing the page URL directly into the browser's address bar. For example, to access the results of poll question id 1, one could go directly to ```/polls/1/results/```. Even worse, the link can be shared on a public forum exposing poll data that is meant to be seen only by authorized users.
#### How to Fix It
Add a ```@method_decorator(login_required, name='dispatch')``` decorator to the ```ResultsView```` class to make sure that only authenticated users can access the results page:
```
@method_decorator(login_required, name='dispatch')
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
```
This decorator enforces that access to each results view is granted only when a user is logged in, fixing the broken access control flaw.

