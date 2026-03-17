#!/usr/bin/env python3
"""
Check sklearn model files
"""

import pickle
import os

def check_model_files():
    """Check if sklearn model files have data"""
    
    print("🔍 CHECKING SKLEARN MODEL FILES")
    print("=" * 40)
    
    model_files = [
        "models/job_category_model.pkl",
        "models/job_title_vectorizer.pkl", 
        "models/normalization_map.pkl"
    ]
    
    for file_path in model_files:
        print(f"\n📁 {file_path}")
        
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   Size: {size} bytes")
            
            if size > 0:
                try:
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    print(f"   ✅ Loaded successfully")
                    print(f"   📊 Type: {type(data)}")
                    
                    if hasattr(data, '__len__'):
                        print(f"   📏 Length: {len(data)}")
                    
                    if hasattr(data, 'classes_'):
                        print(f"   🏷️  Classes: {data.classes_}")
                    
                    if hasattr(data, 'vocabulary_'):
                        print(f"   📚 Vocabulary size: {len(data.vocabulary_)}")
                    
                    if isinstance(data, dict):
                        print(f"   🔑 Keys: {list(data.keys())[:5]}...")
                        print(f"   📏 Dict size: {len(data)}")
                        
                except Exception as e:
                    print(f"   ❌ Error loading: {e}")
            else:
                print(f"   ❌ File is empty (0 bytes)")
        else:
            print(f"   ❌ File not found")
    
    # Test loading and using the models
    print(f"\n🧪 TESTING MODEL FUNCTIONALITY")
    print("=" * 40)
    
    try:
        # Load models
        with open("models/job_category_model.pkl", 'rb') as f:
            model = pickle.load(f)
        
        with open("models/job_title_vectorizer.pkl", 'rb') as f:
            vectorizer = pickle.load(f)
        
        with open("models/normalization_map.pkl", 'rb') as f:
            norm_map = pickle.load(f)
        
        # Test prediction
        test_titles = ["Senior Data Analyst", "Java Developer", "Business Analyst"]
        
        print(f"📝 Test titles: {test_titles}")
        
        # Vectorize
        X_test = vectorizer.transform(test_titles)
        print(f"✅ Vectorized: {X_test.shape}")
        
        # Predict
        predictions = model.predict(X_test)
        print(f"🎯 Predictions: {predictions}")
        
        # Check normalization
        for title in test_titles:
            if title in norm_map:
                print(f"📋 {title} → {norm_map[title]}")
            else:
                print(f"📋 {title} → No normalization")
        
        print(f"\n✅ ALL MODELS WORKING CORRECTLY")
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")

if __name__ == "__main__":
    check_model_files()
