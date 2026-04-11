#!/usr/bin/env python3
"""
Custom test examples for your model
"""

from test_model_accuracy import test_model_with_text

def test_my_examples():
    """Test with your custom examples"""
    
    examples = [
        # Your actual resume examples
        """
        Software Developer
        Lalataksha Consulting Services Pvt Ltd
        Jan 2024 - Present
        Developed and maintained web applications using React.js and Node.js
        """,
        
        """
        React Developer
        Gatnix Technologies Pvt Ltd
        Jun 2022 - Dec 2023
        Implemented dynamic forms and dashboards
        Optimized application performance
        """,
        
        """
        Junior Web Developer
        Disha IT Consultant
        Apr 2021 - May 2022
        Built static and dynamic web pages
        Assisted in frontend features
        """,
        
        # Education examples
        """
        Bachelor of Technology
        Computer Science Engineering
        IIT Delhi
        2017 - 2021
        """,
        
        """
        Master of Science
        Data Science
        Stanford University
        2021 - 2023
        """,
        
        # Complex examples
        """
        Senior Full Stack Developer
        Microsoft Corporation
        Seattle, WA
        Jan 2020 - Present
        Led development of cloud-native applications
        Managed team of 5 developers
        Implemented microservices architecture
        """,
        
        """
        Data Scientist
        Amazon Web Services
        San Francisco, CA
        Jun 2018 - Dec 2019
        Built machine learning models
        Analyzed big data using Python and TensorFlow
        """
    ]
    
    print("="*80)
    print("TESTING MY CUSTOM EXAMPLES")
    print("="*80)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE {i}:")
        print(f"{'='*80}")
        
        test_model_with_text(example.strip(), show_details=True)
        
        print("\n" + "="*80)
        input("Press Enter to continue to next example...")

if __name__ == "__main__":
    test_my_examples()
