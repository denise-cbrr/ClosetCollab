Create a virtual environment using:
  python -m venv .venv
  
  source .venv/bin/activate  # On Mac/Linux
  
  .venv\Scripts\activate     # On Windows
  
  pip install -r requirements.txt

  // to resolve .db issues
  git checkout --theirs closet.db
  git add closet.db
  git commit -m "Resolved conflict in closet.db using theirs"

ty chatgpt
