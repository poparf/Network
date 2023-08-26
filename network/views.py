from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, UserPost,UserFollowing, PostLike
from .forms import UserPostForm
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
import json
from django.shortcuts import get_object_or_404

def index(request):
    allPosts = UserPost.objects.order_by('-timestamp')
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        user = request.user
        liked_posts = PostLike.objects.filter(user=user).values_list('post__id', flat=True)
    
        return render(request, "network/index.html", {
            'allPosts': allPosts,
            'UserPostForm': UserPostForm(),
            "page_obj": page_obj,
            "likedPosts":list(liked_posts)
        })
    else:
        return render(request, "network/index.html", {
            'allPosts': allPosts,
            'UserPostForm': UserPostForm(),
            "page_obj": page_obj
            })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    else:
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            if password != confirmation:
                return render(request, "network/register.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                return render(request, "network/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/register.html")




def createpost(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            UserPostForm_Posted = UserPostForm(request.POST)
            
            if UserPostForm_Posted.is_valid():
                UserPostData = UserPostForm_Posted.save(commit=False)
                user = request.user
                UserPostData.user = user
                UserPostData.save()

                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "network/index.html", {
                'UserPostForm': UserPostForm(),
                "message": 1
            })
        else:
            return render(request, "network/createpost.html", {
                'UserPostForm': UserPostForm()
            })
    else:
        return HttpResponseRedirect(reverse("register"))
    

def userprofile(request, username):
    user = User.objects.get(username=username)
    posts = UserPost.objects.order_by('-timestamp').filter(user=user)
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    followingUsers = UserFollowing.objects.filter(user_id=user)  # all persons that te users follow
    followersUsers = UserFollowing.objects.filter(following_user_id=user) # all persons that follow an user

    try:
        checkFollow = UserFollowing.objects.get(user_id=request.user, following_user_id=user)
        isFollowing = checkFollow  # If the get() operation succeeds, the user is following.
    except:
        isFollowing = False  # If the user is not following, handle the exception.


    return render(request, "network/userprofile.html", {
        "profile":user,
        "followers":followersUsers,
        "following":followingUsers,
        "posts":posts,
        "page_obj": page_obj,
        "isFollowing":isFollowing
    })


def follow(request):
    UserFollowing.objects.create(user_id=request.user, following_user_id=User.objects.get(username=request.POST["userfollow"]))
    return HttpResponseRedirect(reverse("userprofile", args=[User.objects.get(username=request.POST["userfollow"]).username]))

def unfollow(request):
    UserFollowing.objects.get(user_id=request.user, following_user_id=User.objects.get(username=request.POST["userfollow"])).delete()
    return HttpResponseRedirect(reverse("userprofile", args=[User.objects.get(username=request.POST["userfollow"]).username]))

@login_required
def following(request):
    # get all users that the request.user follows
    # get all posts from these users

    followingUsers = UserFollowing.objects.filter(user_id=request.user)
    allPosts = []
    for flwUser in followingUsers:
        allPosts += UserPost.objects.filter(user=flwUser.following_user_id)
    

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    return  render(request, "network/following.html", {
        "page_obj":page_obj
    })


@login_required
def editpost(request,postid):

    userPostInfo = UserPost.objects.get(pk=postid)

    if request.user != userPostInfo.user:
       return HttpResponseRedirect(reverse('index'))



    if request.method == "POST":
       userPostInfo.content = request.POST['content']
       userPostInfo.save(force_update=True)
       return HttpResponseRedirect(reverse('index'))


    return render(request, "network/edit.html", {
        "postform":UserPostForm(initial={'content': userPostInfo.content}),
        "userpost": userPostInfo
    })

@csrf_exempt
@login_required
def postinfo(request, postid):
    
    try:
        post = UserPost.objects.get(pk=postid)
    except UserPost.DoesNotExist:
        return JsonResponse({
            "error": "Post not found."}, status=404)
    
    if request.method == "GET":
        return JsonResponse(post.serialize())
    
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("likes") is not None:
            post.likes = data["likes"]
        post.save()
        return HttpResponse(status=204)
    
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)
    






@login_required
def toggle_like_view(request, postid):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    # Get the UserPost object for the specified postid
    
    post = UserPost.objects.get(id=postid)
    
    if request.method == "GET":
        # Check if the user has liked the post
        liked = PostLike.objects.filter(user=request.user, post=post).exists()

        return JsonResponse({"liked": liked, "likes": post.likes})

    elif request.method == "POST":
        # Toggle the like status for the post
        liked, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if created:
            post.likes += 1
        else:
            liked.delete()
            post.likes -= 1
        post.save()

        return JsonResponse({"liked": not created, "likes": post.likes})

    else:
        return JsonResponse({"error": "GET or POST request required."}, status=400)

