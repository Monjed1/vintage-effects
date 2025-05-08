# GitHub Setup Guide

Follow these steps to push your Vintage Video Effects API to GitHub.

## Prerequisites

1. Install Git from [git-scm.com](https://git-scm.com/downloads)
2. Create a GitHub account if you don't have one at [github.com](https://github.com/join)

## Steps to Push to GitHub

### 1. Install Git

Download and install Git from [git-scm.com/downloads](https://git-scm.com/downloads).

After installation, open a new terminal/command prompt to ensure Git is available.

### 2. Create a New Repository on GitHub

1. Log in to [GitHub](https://github.com)
2. Click the "+" icon in the top-right corner and select "New repository"
3. Enter a name for your repository (e.g., "vintage-video-effects")
4. Optionally add a description
5. Choose whether to make it public or private
6. Do NOT initialize with a README, .gitignore, or license (we'll push our existing code)
7. Click "Create repository"

### 3. Initialize Git in Your Project

Open a terminal/command prompt in your project directory (`C:\Users\kingm\Desktop\monjed\code\Vintage Effect Videos`) and run:

```
git init
```

### 4. Add Your Files to Git

```
git add .
```

This adds all files to the staging area except those in the .gitignore file.

### 5. Commit Your Changes

```
git commit -m "Initial commit with working vintage video effects API"
```

### 6. Link Your Local Repository to GitHub

GitHub will show you the commands after creating the repository. They will look something like:

```
git remote add origin https://github.com/yourusername/vintage-video-effects.git
```

Run this command in your terminal.

### 7. Push Your Code to GitHub

```
git push -u origin master
```

Or if you're using the "main" branch:

```
git push -u origin main
```

You may be prompted to log in to your GitHub account.

## Troubleshooting

### Git is not recognized as a command

If you see "git is not recognized as a command", you need to:
1. Make sure Git is installed
2. Close and reopen your terminal/command prompt
3. If it still doesn't work, you may need to add Git to your PATH environment variable

### Authentication Issues

If you have trouble authenticating:
1. GitHub now uses personal access tokens instead of passwords for authentication
2. Go to GitHub → Settings → Developer settings → Personal access tokens
3. Generate a new token with appropriate permissions
4. Use this token as your password when prompted

## Next Steps

After pushing your code:
1. Add collaborators if needed (in repository settings)
2. Set up GitHub Actions for CI/CD (optional)
3. Enable GitHub Pages if you want to host documentation 