from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import Project, FeatureProject, Profile, Donation, Comment, Rating


# Home Page (Requires Login)
def home(request):
    return render(request, "home/home.html")


# Reset Page
def reset(request):
    return render(request, 'reset/reset.html')


# Project List (All Projects)
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project/project_list.html', {'projects': projects})


# Project Details
def details(request, id):
    project = get_object_or_404(Project, pk=id)
    return render(request, 'project/details.html', {'project': project})


# List of Featured Projects
def featureprojectlist(request):
    projects = FeatureProject.objects.all()
    return render(request, 'project/featureprojectlist.html', {'projects': projects})


# Featured Project Details
def details_featureprojectlist(request, id):
    project = get_object_or_404(FeatureProject, pk=id)
    return render(request, 'project/Featuredetails.html', {'project': project})


# Upload a New Project
@login_required(login_url='signin')
def upload_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            profile, created = Profile.objects.get_or_create(user=request.user)
            project.profile = profile
            project.save()
            messages.success(request, "Project uploaded successfully!")
            return redirect('project_list')
        else:
            messages.error(request, "There were errors in your form. Please fix them below.")
    else:
        form = ProjectForm()

    return render(request, 'project/upload_project.html', {'form': form})


# Update Existing Project
@login_required(login_url='signin')
def update_project(request, id):
    project = get_object_or_404(Project, pk=id)
    
    # Ensure user is the project owner
    if project.owner != request.user:
        messages.error(request, "You are not authorized to update this project.")
        return redirect('project_list')
    
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('project_list')
        else:
            messages.error(request, "There were errors in the form. Please fix them below.")
    
    return render(request, 'project/update_project.html', {'form': form})


# Delete Project
@login_required(login_url='signin')
def delete_p(request, id):
    project = get_object_or_404(Project, pk=id)
    
    # Ensure user is the project owner
    if project.owner != request.user:
        messages.error(request, "You cannot delete another user's project.")
        return redirect('project_list')
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect('project_list')
    
    return render(request, 'project/delete.html', {'project': project})


# Donate to a Project
def donate_to_project(request, id):
    project = get_object_or_404(Project, id=id)
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            if amount > 0:
                profile = request.user.profile if request.user.is_authenticated else Profile.objects.get_or_create(user=None)[0]
                Donation.objects.create(profile=profile, amount=amount, title=f"Donation to {project.title}", project=project)
                project.collectedAmount += amount
                project.save()
                messages.success(request, "Thank you for your donation!")
            else:
                messages.error(request, "Please enter a valid amount.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
        
        return redirect('details', id=project.id)
    
    return redirect('details', id=project.id)


# Comment on a Project
def comment_on_project(request, id):
    project = get_object_or_404(Project, id=id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(project=project, content=content)
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Comment cannot be empty.")
        return redirect('details', id=project.id)


# Rate a Project
def rate_project(request, id):
    project = get_object_or_404(Project, id=id)
    if request.method == 'POST':
        try:
            stars = int(request.POST.get('stars'))
            if 1 <= stars <= 5:
                Rating.objects.create(project=project, stars=stars)
                messages.success(request, "Rating submitted successfully!")
            else:
                messages.error(request, "Rating must be between 1 and 5.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating value.")
        
        return redirect('details', id=project.id)


# User Sign-In
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            auth_login(request, user)
            if 'rememberMe' in request.POST:
                request.session.set_expiry(1209600)  # 2 weeks session
            messages.success(request, f"Welcome, {username}!")
            return redirect('profile_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')
    
    return render(request, "SignIn/signin.html")


# User Sign-Up
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phn_number = request.POST.get('phn_number')

        # Validate passwords
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password1
        )

        # Create or link the profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phn_number = phn_number
        profile.save()

        # Log the user in
        messages.success(request, "Account created successfully!")
        auth_login(request, user)
        return redirect('signin')

    return render(request, "signup/signup.html")


# Profile Dashboard
@login_required
def profile_dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    projects = profile.projects.all()
    
    # Add statistics to each project (like total donations)
    for project in projects:
        project.donations_count = project.donations.count()
        project.donations_total = sum(donation.amount for donation in project.donations.all())
    
    return render(request, "profile/profile.html", {"profile": profile, "projects": projects})

@login_required
def delete_profile(request):
    print(f"Request method: {request.method}")  # Debugging line
    if request.method == "POST":
        try:
            user = request.user
            print(f"User: {user}")  # Debugging line
            
            # Deleting the user
            user.delete()
            print("User deleted successfully")  # Debugging line
            
            # Log out the user after account deletion
            logout(request)
            
            # Provide success message
            messages.success(request, "Your account has been deleted successfully.")
            
            # Redirect to the signup page or homepage
            return redirect("signup")
        except Exception as e:
            print(f"Error deleting profile: {e}")  # Debugging line
            messages.error(request, "An error occurred while trying to delete your account.")
            return redirect("profile_dashboard")
    else:
        print("Invalid request method.")  # Debugging line
        messages.error(request, "Invalid request method.")
        return redirect("profile_dashboard")
# User Sign-Out
def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('signin')


# Update Profile
@login_required
def update_profile(request):
    try:
        profile = request.user.profile  # Get the profile associated with the logged-in user
    except Profile.DoesNotExist:
        # If profile doesn't exist, show an error message and redirect to signup page
        messages.error(request, "Profile does not exist. Please create a profile first.")
        return redirect('signup')
    
    if request.method == "POST":
        # If the form is submitted via POST, bind the data and files (if any)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_dashboard')  # Redirect to profile dashboard
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        # If it's a GET request, pre-fill the form with the user's profile data
        form = ProfileForm(instance=profile)
    
    # Render the form in the template
    return render(request, "profile/update_profile.html", {"form": form})

# Thank You Page
def thank_you(request):
    return render(request, 'home/thank_you.html')


