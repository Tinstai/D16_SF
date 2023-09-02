from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from .filters import *
from .forms import *
from .models import *


class Profile(LoginRequiredMixin, PermissionRequiredMixin, ListView, ):
    """This is a class-based view that displays a user's profile page with their posts and user data."""
    permission_required = ("bulletin_board.delete_post", "bulletin_board.change_post",)
    raise_exception = False
    model = Post
    template_name = 'page_profile.html'
    context_object_name = 'profile'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data'] = User.objects.filter(id=self.request.user.id)
        context['profile'] = Post.objects.filter(author_id=self.request.user.id).order_by("datetime")
        return context


@login_required
@csrf_protect
def consideration(request):
    """
    This is a view function that handles user feedback on posts and
    allows for filtering and pagination of feedback objects.

    param request:
        The HTTP request object that contains information about the current request,
        including the user making the request, any submitted data, and the requested URL

    return:
        The function `consideration` returns a rendered HTML template `page_consideration.html`
        with a context dictionary containing a form and a paginated list of feedback objects.
        The view also handles POST requests to subscribe or unsubscribe a user from a feedback object.
    """
    feedback_objects = list()
    current_user = request.user.id
    current_user_posts = Post.objects.filter(author_id=current_user)
    header = request.GET.get("header")

    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        feedback = Feedback.objects.get(id=feedback_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Feedback.objects.filter(id=feedback_id).update(user_subscribed=True)
            SubscribeFeedback.objects.create(user=request.user, feedback=feedback)
        elif action == 'unsubscribe':
            Feedback.objects.filter(id=feedback_id).update(user_subscribed=False)
            SubscribeFeedback.objects.filter(user=request.user, feedback=feedback).delete()

    # Filtering and getting objects
    for post in current_user_posts:
        feedback_objects = Feedback.objects.filter(feedback_post_id=post.id).order_by("datetime")
        if header:
            feedback_objects = Feedback.objects.filter(feedback_post_id=post.id,
                                                       feedback_post__header__startswith=header, ).order_by("datetime")

    # Set up pagination
    paginator = Paginator(feedback_objects, 5)
    page = request.GET.get("page")
    paginate_feedbacks = paginator.get_page(page)

    context = {
        "form": FeedbackFilterForm(),
        "objects": paginate_feedbacks,
    }

    return render(request, 'page_consideration.html', context)


class PublishBoard(ListView, ):
    """This is a class that displays a list of posts on a webpage, with filtering options and pagination."""
    model = Post
    ordering = 'datetime'
    template_name = 'page_board.html'
    context_object_name = 'list'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PublishDetail(LoginRequiredMixin, FormMixin, DetailView, ):
    """This is a class that displays the details of a post and
    allows users to add comments, while requiring login authentication."""
    raise_exception = False
    model = Post
    template_name = 'page_detail.html'
    context_object_name = 'detail'
    form_class = FeedbackForm

    def get_success_url(self, **kwargs):
        return reverse_lazy("detail", kwargs={"pk": self.get_object().id})

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.feedback_post = self.get_object()
        self.object.feedback_user = self.request.user
        self.object.save()
        return super().form_valid(form)


class PublishPost(LoginRequiredMixin, PermissionRequiredMixin, CreateView, ):
    """This is a class-based view for creating and publishing a post on
    a bulletin board, with login and permission requirements"""
    permission_required = ("bulletin_board.add_post",)
    raise_exception = False
    form_class = PostForm
    model = Post
    template_name = 'page_create.html'
    success_url = reverse_lazy('board')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class PublishUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, ):
    """This is a class-based view for updating a Post object with a form, requiring
    login and permission, and redirecting to the bulletin board page upon successful submission."""
    permission_required = ("bulletin_board.change_post",)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'page_update.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return render(request, '403.html')
        return super(PublishUpdate, self).dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy("detail", kwargs={"pk": self.get_object().id})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class PublishDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView, ):
    """This is a class-based view for deleting a Post object with required login and permission."""
    permission_required = ("bulletin_board.delete_post",)
    raise_exception = True
    model = Post
    template_name = 'page_delete.html'
    success_url = reverse_lazy('board')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return render(request, '403.html')
        return super(PublishDelete, self).dispatch(request, *args, **kwargs)
