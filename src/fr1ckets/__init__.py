from flask import Flask

app = Flask(__name__)

import fr1ckets.views
import fr1ckets.model.setup
