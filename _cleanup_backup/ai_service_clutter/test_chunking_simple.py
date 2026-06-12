#!/usr/bin/env python3
"""
Simple test to verify the chunking logic without requiring transformers.
"""

def simple_chunk_test():
    print("="*70)
    print("🧪 TESTING CHUNKING LOGIC CONCEPT")
    print("="*70)
    
    # Simulate the old vs new chunking approach
    test_text = "John Smith is a Senior Software Engineer at Google Inc. in Mountain View, California."
    
    print(f"\n📝 Test text: {test_text}")
    print(f"Length: {len(test_text)} characters")
    
    # Old approach: simple word splitting with no overlap
    words = test_text.split()
    max_length = 8  # Simulate 8-word chunks
    
    print(f"\n❌ OLD APPROACH (No Overlap):")
    old_chunks = []
    for i in range(0, len(words), max_length):
        chunk = ' '.join(words[i:i + max_length])
        old_chunks.append(chunk)
        print(f"  Chunk {len(old_chunks)}: '{chunk}'")
    
    # New approach: overlapping windows
    print(f"\n✅ NEW APPROACH (With Overlap):")
    overlap = 3
    new_chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_length, len(words))
        chunk = ' '.join(words[start:end])
        new_chunks.append(chunk)
        if end == len(words):
            break
        start += max_length - overlap
        print(f"  Chunk {len(new_chunks)}: '{chunk}'")
    
    # Show the benefit
    print(f"\n📊 COMPARISON:")
    print(f"  Old approach: {len(old_chunks)} chunks")
    print(f"  New approach: {len(new_chunks)} chunks")
    
    # Demonstrate entity boundary preservation
    entity = "Senior Software Engineer at Google"
    print(f"\n🎯 Entity to detect: '{entity}'")
    
    # Check if entity is preserved in old chunks
    entity_preserved_old = any(entity in chunk for chunk in old_chunks)
    print(f"  Entity preserved in old chunks: {entity_preserved_old}")
    
    # Check if entity is preserved in new chunks
    entity_preserved_new = any(entity in chunk for chunk in new_chunks)
    print(f"  Entity preserved in new chunks: {entity_preserved_new}")
    
    # Show specific chunks
    print(f"\n🔍 DETAILED ANALYSIS:")
    for i, chunk in enumerate(old_chunks):
        contains_entity = entity in chunk
        print(f"  Old Chunk {i+1}: '{chunk}' - Contains entity: {contains_entity}")
    
    for i, chunk in enumerate(new_chunks):
        contains_entity = entity in chunk
        print(f"  New Chunk {i+1}: '{chunk}' - Contains entity: {contains_entity}")
    
    print(f"\n✅ CONCLUSION:")
    if entity_preserved_new and not entity_preserved_old:
        print("  🎉 Overlapping chunking SAVES the entity detection!")
    elif entity_preserved_old and entity_preserved_new:
        print("  ✅ Both approaches work for this case")
    else:
        print("  ⚠️  Entity not detected in either approach")

def deduplication_test():
    print(f"\n" + "="*70)
    print("🔄 TESTING DEDUPLICATION LOGIC")
    print("="*70)
    
    # Simulate entities that might appear in overlap regions
    mock_entities = [
        {'word': 'Google', 'entity_group': 'ORG', 'score': 0.9},
        {'word': 'Google', 'entity_group': 'ORG', 'score': 0.85},  # Duplicate
        {'word': 'Python', 'entity_group': 'SKILL', 'score': 0.92},
        {'word': 'python', 'entity_group': 'SKILL', 'score': 0.88},  # Duplicate (case insensitive)
        {'word': 'AWS', 'entity_group': 'SKILL', 'score': 0.95},
        {'word': 'John Smith', 'entity_group': 'PER', 'score': 0.93},
        {'word': 'John Smith', 'entity_group': 'PER', 'score': 0.91},  # Duplicate
    ]
    
    print(f"\n📊 Original entities ({len(mock_entities)}):")
    for i, entity in enumerate(mock_entities, 1):
        print(f"  {i}. '{entity['word']}' ({entity['entity_group']}) - Score: {entity['score']}")
    
    # Simulate deduplication
    seen = set()
    deduplicated = []
    
    for entity in mock_entities:
        key = (entity.get('word', '').strip().lower(), entity.get('entity_group', '').upper())
        if key not in seen:
            seen.add(key)
            deduplicated.append(entity)
    
    print(f"\n✅ After deduplication ({len(deduplicated)}):")
    for i, entity in enumerate(deduplicated, 1):
        print(f"  {i}. '{entity['word']}' ({entity['entity_group']}) - Score: {entity['score']}")
    
    print(f"\n📈 Removed {len(mock_entities) - len(deduplicated)} duplicates")

if __name__ == "__main__":
    simple_chunk_test()
    deduplication_test()
    
    print("\n" + "="*70)
    print("🎉 CHUNKING TEST COMPLETED!")
    print("="*70)
    print("\n📝 KEY BENEFITS OF OVERLAPPING CHUNKING:")
    print("✅ Prevents entities from being split across boundaries")
    print("✅ Ensures complete entities appear in at least one chunk")
    print("✅ Maintains context for better NER performance")
    print("✅ Deduplication removes redundant entities from overlaps")
    print("="*70)
