# Alternative Certification & Course Dataset Links

## 🔄 **Working Alternatives for Coursera Dataset**

### **1. Coursera Course Dataset (GitHub Alternative)** ⭐ **Primary Alternative**
- **Link**: https://github.com/Siddharth1698/Coursera-Course-Dataset
- **Direct CSV**: https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/master/UCoursera_Courses.csv
- **Content**: 890+ Coursera courses with details
- **Format**: CSV
- **Download**: 
```bash
git clone https://github.com/Siddharth1698/Coursera-Course-Dataset.git
# Or download directly:
wget https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/master/UCoursera_Courses.csv
```

### **2. Hugging Face Coursera Dataset** ⭐ **Good Alternative**
- **Link**: https://huggingface.co/datasets/azrai99/coursera-course-dataset
- **Content**: Coursera courses with extracted skills
- **Format**: CSV/JSON
- **Download**: Free from Hugging Face

### **3. Awesome Certificates Repository** ⭐ **Comprehensive List**
- **Link**: https://github.com/PanXProject/awesome-certificates
- **Content**: 200+ free courses with certificates
- **Format**: Markdown list (can be converted to CSV)
- **Categories**: IT, CS, Design, Business
- **Download**: 
```bash
git clone https://github.com/PanXProject/awesome-certificates.git
```

### **4. EdX Dataset (GitHub)** ⭐ **MOOC Alternative**
- **Link**: https://github.com/MainakRepositor/Datasets/blob/master/EdX.csv
- **Direct CSV**: https://raw.githubusercontent.com/MainakRepositor/Datasets/master/EdX.csv
- **Content**: EdX courses dataset
- **Format**: CSV
- **Download**: 
```bash
wget https://raw.githubusercontent.com/MainakRepositor/Datasets/master/EdX.csv
```

### **5. Free Certifications Collection** ⭐ **Free Resources**
- **Link**: https://github.com/cloudcommunity/Free-Certifications
- **Content**: Free professional certifications
- **Format**: Markdown list
- **Categories**: Cloud, Cybersecurity, Development
- **Download**: 
```bash
git clone https://github.com/cloudcommunity/Free-Certifications.git
```

## 🎯 **Professional Certification Databases**

### **6. IBM Professional Certifications**
- **Link**: https://github.com/ndohvich/IBM-Data-Science-Professional-Certificate
- **Content**: IBM certification programs and skills
- **Format**: Repository with course materials
- **Download**: 
```bash
git clone https://github.com/ndohvich/IBM-Data-Science-Professional-Certificate.git
```

### **7. AWS Certification Resources**
- **Link**: https://github.com/CleitonCorrea/my-certifications
- **Content**: AWS, IBM, Microsoft, Oracle certifications
- **Format**: Repository with certification examples
- **Download**: 
```bash
git clone https://github.com/CleitonCorrea/my-certifications.git
```

## 📊 **Kaggle Alternatives (Working Links)**

### **8. EdX Courses Dataset 2021**
- **Link**: https://www.kaggle.com/datasets/khusheekapoor/edx-courses-dataset-2021
- **Content**: EdX courses from 2021
- **Format**: CSV
- **Requires**: Free Kaggle account

### **9. Udemy Courses Dataset**
- **Link**: https://www.kaggle.com/datasets/hugoromanish/udemy-courses-dataset
- **Content**: Udemy courses with details
- **Format**: CSV
- **Requires**: Free Kaggle account

## 🚀 **Quick Download Script**

```bash
#!/bin/bash
# Download certification and course datasets

echo "Downloading Coursera Course Dataset..."
wget https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/master/UCoursera_Courses.csv

echo "Downloading EdX Dataset..."
wget https://raw.githubusercontent.com/MainakRepositor/Datasets/master/EdX.csv

echo "Cloning Awesome Certificates..."
git clone https://github.com/PanXProject/awesome-certificates.git

echo "Cloning Free Certifications..."
git clone https://github.com/cloudcommunity/Free-Certifications.git

echo "Cloning IBM Certifications..."
git clone https://github.com/ndohvich/IBM-Data-Science-Professional-Certificate.git

echo "All certification datasets downloaded!"
```

## 📁 **Updated Directory Structure**

```
data/
├── external/
│   ├── certifications/
│   │   ├── coursera_courses.csv                    # From GitHub (Siddharth1698)
│   │   ├── edx_courses.csv                         # From GitHub (MainakRepositor)
│   │   ├── awesome_certificates/                   # From GitHub (PanXProject)
│   │   ├── free_certifications/                     # From GitHub (cloudcommunity)
│   │   ├── ibm_certifications/                     # From GitHub (ndohvich)
│   │   ├── udemy_courses.csv                       # From Kaggle
│   │   └── certification_examples/                  # From GitHub (CleitonCorrea)
│   └── work_experience/
│       ├── resume_classification_dataset.csv        # From GitHub (noran-mohamed)
│       ├── fortune500_companies.csv                 # From GitHub (cmusam)
│       └── job_titles_dataset.csv                  # From Kaggle
```

## 💡 **Recommendation**

### **Start with These (Highest Priority):**
1. **Coursera Course Dataset** (GitHub) - Direct CSV download
2. **EdX Dataset** (GitHub) - Direct CSV download  
3. **Awesome Certificates** (GitHub) - Comprehensive list
4. **Resume Classification Dataset** (GitHub) - 13K+ resumes

### **Next Priority:**
5. **Free Certifications** (GitHub) - Additional free resources
6. **Fortune 500 Companies** (GitHub) - Company normalization
7. **Job-Description Matching** (GitHub) - Skills mapping

These alternatives should provide comprehensive coverage for your work experience and certification parsing goals without relying on the broken Kaggle link!
