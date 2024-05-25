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
**how to fix it**<br>
Enable ```'django.middleware.csrf.CsrfViewMiddleware'``` middleware in settings.py and add ```{% csrf_token %}``` to all forms in the html documents. This will make sure that all forms include CSRF tokens protecting the users from unwanted actions performed without their consent.


### FLAW 2: SQL Injection
**exact source link pinpointing flaw 2**
- views.py | class DetailView | def post
- detail.html | second form

**description of flaw 2**<br>
A threat actor can exploit unsanitized SQL handling to inject SQL statements via user forms. In other words, this vulnerability allows the attacker to execute arbitrary SQL commands by manipulating input data.

Example: The threat actor uses the choice creator form to make a new choice while setting an arbitrary vote tally. This injection payload would create a choice "A thousand votes" and set its vote tally to 1000:
```
A thousand votes', 1000); --
```
**how to fix it**
1. Use Django Forms for input Handling:
- In detail.html, instead of the default html form, use ```{{ form.as_p }}``` to make use of Django's form rendering which provides built-in protection against SQL injection.
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
**exact source link pinpointing flaw 2**
- detail.html | {{ comment.comment_text|safe }}

**description of flaw 2**<br>
Cross-Site Scripting (XSS) allows a threat actor to inject malicious scripts into the webpages viewed by other users. The comments section of the poll detail page does not properly escape user input as they are rendered with the safe filter allowing execution of arbitrary HTML or JavaScript code leading to execution of injected script.

Example: Entering the following script to the comments, misguides users to vote for the wrong choice: 
```
<script>alert('Admin notice: There is an error in the poll, choices 1 and 2 have been swapped. Vote 1 for choice 2, and vote 2 for choice 1');</script>
```
Example: Instead of rendering the page normally, render only a h1 header claiming that the poll has been closed, which also prevents the user from voting because the forms are not rendered:
```
<script>document.body.innerHTML = '<h1>This Poll has been closed.</h1>';</script>
```
**how to fix it**<br>
Remove the ```|safe``` filter when rendering comments ensuring that the user-generated content is properly escaped.


### FLAW 4: Broken Authentication
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


### FLAW 5: Insecure Direct Object References (IDOR)
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...

