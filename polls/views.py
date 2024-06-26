from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserRegisterForm, QuestionForm, ChoiceForm, CommentForm

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those se to 
        be published in the future)
        """
        return (Question.objects.filter(pub_date__lte=timezone.now())
                .order_by("-pub_date")[:5])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuestionForm()
        return context
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()  # set pub_date to current time
            question.save()
            return redirect('polls:index')
        return render(request, self.template_name, {'form': form})


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChoiceForm()
        return context
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice_text = form.cleaned_data['choice_text']
            question_id = self.get_object().id
            with connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO polls_choice (question_id, choice_text, votes) VALUES ({question_id}, '{choice_text}', 0)")
            return redirect('polls:detail', pk=question_id)
            # Instead of the above, replace with the following code to use ORM
            # choice = form.save(commit=False)
            # choice.question = self.get_object()
            # choice.save()
            # return redirect('polls:detail', pk=self.get_object().pk)
        return render(request, self.template_name, {'form': form, 'question': self.get_object()})


# @method_decorator(login_required, name='dispatch')
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", 
                                            args=(question.id,)))


def anonymous_required(function=None, redirect_url=None):
    if not redirect_url:
        from django.conf import settings
        redirect_url = settings.LOGIN_REDIRECT_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url,
        redirect_field_name=None
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


@anonymous_required(redirect_url='polls:auth')
def auth_view(request):
    register_form = UserRegisterForm()
    login_form = AuthenticationForm()
    
    if request.method == 'POST':
        if 'register' in request.POST:
            register_form = UserRegisterForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                username = register_form.cleaned_data.get('username')
                password = register_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('polls:index')
        elif 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('polls:index')
    
    return render(request, 'polls/auth.html', {'register_form': register_form, 'login_form': login_form})


def add_comment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.question = question
            # comment.comment_text = escape(comment.comment_text)
            comment.save()
            return redirect('polls:detail', pk=question.id)
    else:
        form = CommentForm()
    return render(request, 'polls/detail.html', {'form': form, 'question': question})
