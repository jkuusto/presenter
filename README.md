# presenter

This web app showcases a demo app, Polls, with 5 security vulnerabilities.


## Table of Contents
- [Setup](#setup)
- [Features](#features)


## Setup

Coming soon.


## Features

### FLAW 1: Cross-Site Request Forgery (CSRF)
**exact source link pinpointing flaw 1**
- index.html | <!-- {% csrf_token %} -->
- detail.html | <!-- {% csrf_token %} -->
- auth.html | <!-- {% csrf_token %} -->
- settings.py | # 'django.middleware.csrf.CsrfViewMiddleware',

**description of flaw 1**<br>
Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on the application where they are logged in. This is because the app does not verify the request's origin.
- The victim is logged into the polling application and has a valid session with the site.
- The victim is tricked into visiting a malicious site created by the attacker.
- The malicious site contains a form that auto-submits a request to the polling application, using the victim's authenticated session.
The polling application processes the request as if it were initiated by the victim. The threat actor may want to manipulate the results of a poll by casting votes without the users' knowledge or they may want to introduce inappropriate or misleading choices to an existing poll question.

Here is an example where the threat actor has tricker the victim to click a link to a site where the victim's authentication is used to automatically vote for choice 1: 
```
<form action="http://localhost:8000/polls/1/vote/" method="post" id="snkeakyForm">
    <input type="hidden" name="choice" value="1">
    <input type="submit" value="Submit Vote">
</form>

<script>
    document.getElementById('sneakyForm').submit();
</script>
```
**how to fix it**<br>
Enable ```'django.middleware.csrf.CsrfViewMiddleware'``` middleware in settings.py and add ```{% csrf_token %}``` to all forms in the html documents. This will make sure that all forms include CSRF tokens protecting the users from unwanted actions performed without their consent.


### FLAW 2: SQL Injection
**exact source link pinpointing flaw 2**
- views.py | class DetailView | def post
- detail.html | second form

**description of flaw 2**<br>
A threat actor can exploit unsanitized SQL handling to inject SQL statements in a user form. This vulnerability allows an attacker to execute arbitrary SQL commands by manipulating input data.

Example: The threat actor uses the choice creator form to make a new choice while setting a desired vote tally. This injection payload would create a choice "A thousand votes" and set the vote tally to 1000:
```
A thousand votes', 1000); --
```
**how to fix it**
1. Use Django Forms for input Handling:
- In detail.html, instead of the default html form, use ```{{ form.as_p }}``` to make use of Django's form rendering providing built-in protection against SQL injection.
2. Use Django's ORM for Database Operations:
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


### FLAW 3: Cross-Site Scripting (XSS)
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


### FLAW 4: Broken Authentication
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


### FLAW 5: Insecure Direct Object References (IDOR)
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...

