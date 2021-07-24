### To Do's
- [ ] Update README, setup.py, requirements.txt
-   

---

<div align="center">    
 
# NotionToTwitter  
 
</div>
 
## Description   
What it does   

## Directory Structure

```
.
+-- globalStore/
|   +-- constants.py
+-- lib/
|   +-- checkpoint_utils.py
|   +-- train_eval_utils.py
|   +-- utils.py
+-- notebooks/
|   +-- __init__.py
+-- outputs/
|   +-- __init__.py
+-- scripts/
|   +-- dummy.sh
+-- src/
|   +-- __init__.py
+-- .gitignore
+-- juyptext.toml
+-- LICENSE
+-- README.md
+-- requirements.txt
```

## How to run   
First, install dependencies   
```bash
# clone project   
git clone https://github.com/YourGithubName/deep-learning-project-template

# install project   
cd deep-learning-project-template 
pip install -e .   
pip install -r requirements.txt
 ```   
 Next, navigate to any file and run it.   
 ```bash
# module folder
cd project

# run module (example: mnist as your main contribution)   
python lit_classifier_main.py    
```

## Imports
This project is setup as a package which means you can now easily import any file into any other file like so:
```python
from project.datasets.mnist import mnist
from project.lit_classifier_main import LitClassifier
from pytorch_lightning import Trainer

# model
model = LitClassifier()

# data
train, val, test = mnist()

# train
trainer = Trainer()
trainer.fit(model, train, val)

# test using the best model!
trainer.test(test_dataloaders=test)
```

## Usage

## References

## Citation   
```
@article{YourName,
  title={Your Title},
  author={Your team},
  journal={Location},
  year={Year}
}
```   
 

