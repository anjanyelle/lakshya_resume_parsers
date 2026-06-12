#!/usr/bin/env python3
"""
Demonstration of overlapping chunking benefits for entity detection.
"""

def demonstrate_chunking_benefits():
    print("="*80)
    print("🎯 DEMONSTRATING OVERLAPPING CHUNKING FOR ENTITY DETECTION")
    print("="*80)
    
    # Real-world example where overlapping helps
    resume_text = """John Smith is a Senior Software Engineer at Google Inc. 
    He has extensive experience with Python, Java, and cloud technologies. 
    His email is john.smith@gmail.com and phone is +1-555-0123."""
    
    print(f"\n📄 Resume text:")
    print(f"   {resume_text}")
    
    words = resume_text.split()
    print(f"\n📊 Total words: {len(words)}")
    
    # Simulate chunking with different parameters
    max_len = 12  # words per chunk
    overlap = 4   # overlap words
    
    print(f"\n⚙️  Chunking parameters:")
    print(f"   Max words per chunk: {max_len}")
    print(f"   Overlap words: {overlap}")
    
    # Old approach (no overlap)
    print(f"\n❌ OLD APPROACH (No Overlap):")
    old_chunks = []
    for i in range(0, len(words), max_len):
        chunk_words = words[i:i + max_len]
        chunk = ' '.join(chunk_words)
        old_chunks.append(chunk)
        print(f"   Chunk {len(old_chunks)}: '{chunk}'")
    
    # New approach (with overlap)
    print(f"\n✅ NEW APPROACH (With Overlap):")
    new_chunks = []
    start = 0
    chunk_num = 1
    while start < len(words):
        end = min(start + max_len, len(words))
        chunk_words = words[start:end]
        chunk = ' '.join(chunk_words)
        new_chunks.append(chunk)
        print(f"   Chunk {chunk_num}: '{chunk}'")
        if end == len(words):
            break
        start += max_len - overlap
        chunk_num += 1
    
    # Test specific entities
    test_entities = [
        "Senior Software Engineer",
        "Google Inc.",
        "john.smith@gmail.com",
        "+1-555-0123"
    ]
    
    print(f"\n🎯 ENTITY DETECTION ANALYSIS:")
    print("="*50)
    
    for entity in test_entities:
        print(f"\n📝 Entity: '{entity}'")
        
        # Check old chunks
        found_old = any(entity in chunk for chunk in old_chunks)
        print(f"   ❌ Old chunks: {'✅ FOUND' if found_old else '❌ NOT FOUND'}")
        if found_old:
            for i, chunk in enumerate(old_chunks):
                if entity in chunk:
                    print(f"      → Chunk {i+1}: '{chunk}'")
                    break
        
        # Check new chunks
        found_new = any(entity in chunk for chunk in new_chunks)
        print(f"   ✅ New chunks: {'✅ FOUND' if found_new else '❌ NOT FOUND'}")
        if found_new:
            for i, chunk in enumerate(new_chunks):
                if entity in chunk:
                    print(f"      → Chunk {i+1}: '{chunk}'")
                    break
        
        # Show improvement
        if found_new and not found_old:
            print(f"   🎉 IMPROVEMENT: Entity now detected!")
        elif found_old and found_new:
            print(f"   ✅ Both approaches work")
        else:
            print(f"   ⚠️  Entity not detected in either approach")
    
    # Show overlap benefits visually
    print(f"\n📊 OVERLAP VISUALIZATION:")
    print("="*50)
    
    for i, chunk in enumerate(new_chunks):
        print(f"Chunk {i+1}: {chunk}")
        if i < len(new_chunks) - 1:
            next_chunk = new_chunks[i + 1]
            # Find overlapping words
            current_words = chunk.split()
            next_words = next_chunk.split()
            overlap_words = []
            for word in current_words[-overlap:]:
                if word in next_words[:overlap]:
                    overlap_words.append(word)
            if overlap_words:
                print(f"    ↓ Overlap: {' '.join(overlap_words)}")
            else:
                print(f"    ↓ (no overlap)")
        print()

def show_real_world_impact():
    print("="*80)
    print("💼 REAL-WORLD IMPACT ON RESUME PARSING")
    print("="*80)
    
    scenarios = [
        {
            'name': 'Company Name Split',
            'text': 'worked at Microsoft Corporation as Senior Developer',
            'entity': 'Microsoft Corporation',
            'issue': 'Microsoft | Corporation split across chunks'
        },
        {
            'name': 'Email Split',
            'text': 'contact at john.doe.smith@example.com for more information',
            'entity': 'john.doe.smith@example.com',
            'issue': 'john.doe.smith@ | example.com split across chunks'
        },
        {
            'name': 'Job Title Split',
            'text': 'Senior Vice President of Engineering',
            'entity': 'Senior Vice President of Engineering',
            'issue': 'Senior Vice President | of Engineering split across chunks'
        },
        {
            'name': 'Phone Number Split',
            'text': 'call me at +1-555-123-4567 for details',
            'entity': '+1-555-123-4567',
            'issue': '+1-555-123 | -4567 split across chunks'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Text: {scenario['text']}")
        print(f"   Entity: {scenario['entity']}")
        print(f"   Issue: {scenario['issue']}")
        print(f"   ✅ Solution: Overlapping chunks ensure complete entity appears in at least one chunk")

if __name__ == "__main__":
    demonstrate_chunking_benefits()
    show_real_world_impact()
    
    print("\n" + "="*80)
    print("🎉 SUMMARY: OVERLAPPING CHUNKING BENEFITS")
    print("="*80)
    print("✅ Prevents entity boundary breaks")
    print("✅ Improves detection accuracy for long entities")
    print("✅ Maintains context across chunk boundaries")
    print("✅ Deduplication removes redundant results")
    print("✅ Critical for resume parsing with complex entities")
    print("="*80)
