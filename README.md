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
views.py | class DetailView |  @method_decorator(csrf_exempt) def post
detail.html | <!-- {% csrf_token %} -->
**description of flaw 1**
A threat actor can exploit CSRF vulnerabilities to perform unauthorized actions on behalf of an authenticated user.
The victim is logged into the polling application and has a valid session with the site.
The victim is tricked into visiting a malicious site created by the attacker.
The malicious site contains a form that auto-submits a request to the polling application, leveraging the victim's authenticated session.
The polling application processes the request as if it were initiated by the victim, thus performing the action without the victim's knowledge. For example, the threat actor wants to manipulate the results of a poll by casting votes without the users' knowledge, or The threat actor wants to introduce inappropriate or misleading choices to an existing poll question.
**how to fix it**
Remove the @method_decorator(csrf_exempt) decorator in views.py and add {% csrf_token %} to the forms on detail.html.


FLAW 2: SQL Injection
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


FLAW 3: Cross-Site Scripting (XSS)
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


FLAW 4: Broken Authentication
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...


FLAW 5: Insecure Direct Object References (IDOR)
exact source link pinpointing flaw 2...
description of flaw 2...
how to fix it...

