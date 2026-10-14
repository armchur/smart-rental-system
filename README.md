# Smart Rental System for Automated Equipment Recognition and Management

[![Python Version](https://img.shields.io/badge/Python-3.11.9-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Backend-Django_5.2-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Flask](https://img.shields.io/badge/AI_Microservice-Flask_3.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/Deep_Learning-TensorFlow_2.21_/_VGG16-FF6F00.svg?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-Academic_Research-green.svg)]()

> **Final Year Project (B.Tech Computer Science)**  
> **Department of Computer Science**, Modibbo Adama University (MAU), Yola, Adamawa State, Nigeria  
> **Researcher:** Armstrong Finchur  
> **Topic:** *Smart Rental System for Automated Production Recognition and Management, Using Conventional Network of Image Classification*

---

## 📋 Abstract & Overview

Informal and semi-formal equipment rental enterprises in developing economies rely predominantly on manual ledgers and subjective visual inspection for tool identification, inventory auditing, and dispatch tracking. This reliance causes recurring stock misidentification, billing inaccuracies, prolonged turnaround times, and untracked depreciation.

The **Smart Rental System** addresses these operational bottlenecks by integrating deep learning computer vision with a decoupled three-tier enterprise resource planning (ERP) web architecture:
- **Computer Vision Core:** A fine-tuned **VGG16** Deep Convolutional Neural Network (CNN) classifying 8 industrial and construction equipment categories.
- **Decision Engine:** Evaluates visual inferences against a **65.0% confidence threshold** and computes **Top-3 ranking** candidates.
- **Enterprise Web Tier:** A **Django** web application coordinating real-time stock allocation, duration-based pricing, customer dispatch agreements, and equipment return lifecycles.

---

## 🏛️ System Architecture

The platform uses a decoupled client-server microservice topology:

```text
       +-------------------------------------------------------------+
       |                     Operator Interface                      |
       |       (Bootstrap 5 Responsive Web UI / Desktop & Mobile)    |
       +------------------------------+------------------------------+
                                      |
                           HTTP / Multipart POST
                                      v
       +-------------------------------------------------------------+
       |                   Django Web Core (Port 8000)               |
       |  - Equipment Inventory Catalog    - Customer Registry       |
       |  - Automated Dispatch Engine      - Rental History & Audits |
       +---------------+------------------------------+--------------+
                       |                              |
            Internal REST Proxy                 Relational ORM
          (POST image payload)                        |
                       v                              v
       +-------------------------------+   +-------------------------+
       | Flask AI Service (Port 5000)  |   | 3NF Relational Database |
       | - VGG16 Transfer Learning     |   | - Equipment             |
       | - Preprocessing (224x224)     |   | - Categories (8 classes)|
       | - 65% Confidence Filter       |   | - Customers             |
       | - Top-3 Softmax Probabilities |   | - Rental Agreements     |
       +-------------------------------+   | - Recognition Logs      |
                                           +-------------------------+


🤖 Deep Learning Model Specifications
Parameter	Specification
Base Architecture	VGG16 (ImageNet pre-trained feature extractor, frozen)
Classification Head	Flatten 
→
→ Dense (256 ReLU) 
→
→ Dropout (0.5) 
→
→ Softmax (8 units)
Input Dimensions	
224
×
224
×
3
224×224×3 RGB (Normalized to $[0, 1]$)
Training Epochs	10 Epochs (Adam Optimizer, Learning Rate = $0.0001$, Batch Size = 16)
Validation Accuracy	86.4%
Benchmark Sample Confidence	87.13% (Field-verified on industrial generators)
Decision Threshold	
≥
0.65
≥0.65 ($65.0%$ minimum operational acceptance)
Inference Latency	
∼
1.18
∼1.18 seconds on CPU
Target Equipment Classes
generator
concrete_mixer
welding_machine
electric_drill
water_pump
chainsaw
lawn_mower
air_compressor


🚀 Key Functional Features
Automated AI Scan & Stock Matching: Upload an equipment photo 
→
→ the system classifies the machine type 
→
→ queries database in real-time 
→
→ displays only units currently marked as Available.
Automated Billing Engine: Dynamic calculation of rental durations and total costs based on daily rates: 
Total Amount
=
Daily Rate
×
(
Expected Return Date
−
Rental Date
)
Total Amount=Daily Rate×(Expected Return Date−Rental Date)
Real-Time Inventory Status Synchronization:
On dispatch: Equipment status immediately flips from AVAILABLE 
→
→ RENTED.
On return: Attendant clicks "Return Unit" 
→
→ status updates to AVAILABLE, instantly restoring it to the catalog and future AI scans.
Recognition Audit Trail: Every scan is permanently registered in RecognitionLog with upload timestamps, predicted class, and exact confidence percentages for supervisor auditing.



🛠️ Tech Stack & Dependencies
Programming Language: Python 3.11.9
Web Backend: Django 5.2.x
AI Microservice: Flask 3.1.x
Deep Learning Framework: TensorFlow 2.21.x / Keras
Numerical Processing: NumPy 1.26.4
Computer Vision & Imaging: Pillow (PIL) 12.3.x
Frontend: HTML5, CSS3, Bootstrap 5, Jinja2 / Django Templates
Database: SQLite (development / local demo) / PostgreSQL-ready


💻 Installation & Local Setup


Prerequisites




Python 3.11 installed (make sure Add python.exe to PATH is checked)


Git installed


Microsoft Visual C++ 2015–2022 Redistributable (x64)




1. Clone the Repository


git clone https://github.com/armchur/smart-rental-system.git
cd smart-rental-system



2. Set Up Virtual Environment


# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate



3. Install Dependencies


python -m pip install --upgrade pip
pip install -r requirements.txt



4. Database Setup & Seeding


python manage.py makemigrations rental_app
python manage.py migrate
python seed_data.py



5. Add Trained Model Weights



Due to GitHub file size limits, model weights (*.keras) are stored locally:





Place your trained model file at: model/smart_rental_vgg16.keras


Place category mappings at: model/class_labels.json






🏃 Running the Application



To run the full end-to-end system, two services must run concurrently:



Terminal 1: Flask Deep Learning Service (Port 5000)


venv\Scripts\activate
python app/recognition_service.py




Health Check: Active on http://127.0.0.1:5000/predict



Terminal 2: Django Web Application (Port 8000)


venv\Scripts\activate
python manage.py runserver




Web Application Portal: Open http://127.0.0.1:8000/ in your browser.





📸 System Walkthrough & User Flow




Inventory Catalog (/): Browse live equipment inventory with status badges (Available, Currently Rented, Maintenance).


AI Equipment Scanner (/scan/): Submit a photo of tools brought to the counter. The VGG16 model returns class name, confidence bar, Top-3 distribution, and matching available stock.


Dispatch Agreement (/book/<id>/): Select customer, set dates, review auto-computed totals, and dispatch unit.


Rental History & Auditing (/history/): View all active and concluded agreements; process returns with a single click.






📂 Project Directory Structure


smart-rental-system/
├── app/
│   └── recognition_service.py      # Flask REST API for VGG16 inference
├── model/
│   ├── class_labels.json           # JSON list of 8 equipment class names
│   └── smart_rental_vgg16.keras    # Trained model weights (local)
├── rental_app/
│   ├── migrations/                 # Database schema migrations
│   ├── templates/rental_app/       # Bootstrap 5 HTML templates
│   │   ├── base.html               # Master layout and navigation
│   │   ├── equipment_list.html     # Inventory catalog view
│   │   ├── scan.html               # AI recognition upload & results
│   │   ├── book_rental.html        # Rental dispatch form
│   │   └── rental_history.html     # Rental history and returns
│   ├── admin.py                    # Django administration bindings
│   ├── models.py                   # 3NF schema (Equipment, Rental, Customer, Log)
│   ├── urls.py                     # App routing configurations
│   └── views.py                    # Business logic and microservice proxy
├── smartrental_web/
│   ├── settings.py                 # Django project settings
│   ├── urls.py                     # Root routing table
│   └── wsgi.py
├── .gitignore                      # Git exclusion rules
├── manage.py                       # Django CLI management script
├── requirements.txt                # Pinned Python package dependencies
├── seed_data.py                    # Initial database population script
└── README.md                       # System documentation





🎓 Academic Attribution & Citation



If you use or reference this system in related academic work or research, please cite as:



@mastersthesis{finchur2026smartrental,
  author       = {Finchur, Armstrong},
  title        = {Smart Rental System for Automated Production Recognition and Management, Using Conventional Network of Image Classification},
  school       = {Department of Computer Science, Modibbo Adama University},
  year         = {2026},
  address      = {Yola, Adamawa State, Nigeria},
  type         = {B.Tech Project Report}
}





📄 License



This project was developed solely for academic research, evaluation, and educational demonstration at Modibbo Adama University, Yola. All rights reserved by the author.
