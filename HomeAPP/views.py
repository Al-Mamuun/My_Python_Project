from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import *

# Home Page (Requires Login)

def home(request):
    return render(request, template_name="home/home.html")

# Reset Page
def reset(request):
    return render(request, template_name='reset/reset.html')

# List All Projects
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project/project_list.html', {'projects': projects})

# Project Details
def details(request, id):
    project = get_object_or_404(Project, pk=id)
    return render(request, 'project/details.html', {'project': project})

# List Featured Projects
def featureprojectlist(request):
    projects = FeatureProject.objects.all()
    return render(request, 'project/featureprojectlist.html', {'projects': projects})

# Featured Project Details
def details_featureprojectlist(request, id):
    project = get_object_or_404(FeatureProject, pk=id)
    return render(request, 'project/Featuredetails.html', {'project': project})


# Upload a New Project
@login_required(login_url='signin')  # Redirects to the login page if the user is not authenticated
def upload_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            # Do not directly save the form. Use commit=False to modify the instance first.
            project = form.save(commit=False)
            
            # Link the project to the current user's profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            project.profile = profile  # Assign the profile to the project
            
            project.save()  # Save the project instance
            messages.success(request, "Project uploaded successfully!")
            return redirect('project_list')
        else:
            messages.error(request, "There were errors in your form. Please fix them below.")
    else:
        form = ProjectForm()

    return render(request, 'project/upload_project.html', {'form': form})

# Update Existing Project
# Update Project
@login_required(login_url='signin')  # Redirects to the login page if not logged in
def update_project(request, id):
    update = get_object_or_404(Project, pk=id)
    
    # Check if the logged-in user is the owner of the project
    if update.owner != request.user:  # Replace `owner` with the field in your Project model that relates to the user
        messages.error(request, "You are not authorized to update this project.")
        return redirect('project_list')  # Redirect to an appropriate page, e.g., project list or details
    
    form = ProjectForm(instance=update)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('project_list')
        else:
            messages.error(request, "There were errors in the form. Please fix them below.")
    
    return render(request, 'project/update_project.html', {'form': form})

# Delete Project
@login_required(login_url='signin')  # Redirects to the login page if not logged in
def delete_p(request, id):
    project = get_object_or_404(Project, pk=id)
    
    # Check if the logged-in user is the owner of the project
    if project.owner != request.user:  # Replace `owner` with the field in your Project model that relates to the user
        messages.error(request, "You cannot delete another user's project.")
        return redirect('project_list')  # Redirect to an appropriate page, e.g., project list or details
    
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
                # Check if the user is authenticated
                if request.user.is_authenticated:
                    profile = request.user.profile  # Get the authenticated user's profile
                else:
                    # Handle guest users by using a default or guest profile
                    # You can create a default profile if you want to track guest donations separately
                    profile, created = Profile.objects.get_or_create(user=None)  # Create a guest profile

                    # Optionally, you could also create a unique guest profile for each session
                    # profile, created = Profile.objects.get_or_create(user=None, session_key=request.session.session_key)
                    
                # Create the donation
                Donation.objects.create(
                    profile=profile,  # Profile (either user profile or guest profile) should be assigned
                    amount=amount,
                    title=f"Donation to {project.title}",
                    project=project  # Link donation to the project
                )

                # Update the project's collected amount
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

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            
            # Handle "Remember me"
            if 'rememberMe' in request.POST:
                request.session.set_expiry(1209600)

            messages.success(request, f"Welcome, {username}!")
            return redirect('profile_dashboard')  # Redirect to the profile dashboard
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

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password1,
        )

        # Check if profile already exists
        if not Profile.objects.filter(user=user).exists():
            # Create the profile if it doesn't exist
            profile = Profile.objects.create(user=user, phn_number=phn_number)

        messages.success(request, "Account created successfully! You are logged in now.")

        # Log the user in automatically
        auth_login(request, user)

        # Redirect the user to the profile page or dashboard
        return redirect('signin')

    return render(request, "signup/signup.html")



@login_required
def profile_dashboard(request):
    # Ensure the user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Get all the projects associated with this profile
    projects = profile.projects.all()

    # Optional: Add statistics to each project (like total donations)
    for project in projects:
        # Calculate the total donations for this project
        project.donations_count = project.donations.count()  # Example: number of donations
        project.donations_total = sum(donation.amount for donation in project.donations.all())  # Example: total donation amount

    # Pass the profile and projects (with statistics) to the template
    return render(request, "profile/profile.html", {"profile": profile, "projects": projects})




def signout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('signin')  # Redirect to the sign-in page after logout


@login_required
def update_profile(request):
    try:
        profile = request.user.profile  # Get the user's profile
    except Profile.DoesNotExist:
        # If the profile does not exist, redirect to profile creation
        messages.error(request, "Profile does not exist. Please create a profile first.")
        return redirect('signup')  # or a profile creation view if needed

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_dashboard')  # Redirect to profile dashboard after saving
        else:
            messages.error(request, "There was an error updating your profile.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile/update_profile.html", {"form": form})


def thank_you(request):
    return render(request, 'home/thank_you.html')