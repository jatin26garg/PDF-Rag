"""
Test script for File System Tools.
Run this to verify everything works.
"""

from pathlib import Path
from app.tools.file_tools import create_file_tool


def test_file_tools():
    """Test all file system operations."""
    
    print("\n" + "="*60)
    print("📁 FILE SYSTEM TOOL - TEST SUITE")
    print("="*60)
    
    tool = create_file_tool()
    print(f"📂 Workspace: {tool.workspace}\n")
    
    # ===========================================
    # Test 1: Write a text file
    # ===========================================
    print("📝 Test 1: Write a text file")
    print("-"*40)
    
    result = tool.write_file(
        path="outputs/test.txt",
        content="Hello! This is a test file.\nCreated by the File System Tool."
    )
    print(f"   Success: {result['success']}")
    print(f"   Path: {result.get('path', 'N/A')}")
    print(f"   Size: {result.get('size', 0)} bytes\n")
    
    # ===========================================
    # Test 2: Write a JSON file
    # ===========================================
    print("📝 Test 2: Write a JSON file")
    print("-"*40)
    
    json_content = '{"name": "Test", "value": 123, "active": true}'
    result = tool.write_file(
        path="outputs/data.json",
        content=json_content
    )
    print(f"   Success: {result['success']}")
    print(f"   Path: {result.get('path', 'N/A')}\n")
    
    # ===========================================
    # Test 3: Read the text file
    # ===========================================
    print("📖 Test 3: Read a file")
    print("-"*40)
    
    result = tool.read_file("outputs/test.txt")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Content: {result['content'][:50]}...")
        print(f"   Size: {result['size']} bytes\n")
    
    # ===========================================
    # Test 4: List files
    # ===========================================
    print("📋 Test 4: List files")
    print("-"*40)
    
    result = tool.list_files("outputs")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Files: {result['files']}")
        print(f"   Directories: {result['directories']}\n")
    
    # ===========================================
    # Test 5: Get file info
    # ===========================================
    print("ℹ️ Test 5: Get file info")
    print("-"*40)
    
    result = tool.get_file_info("outputs/test.txt")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Path: {result['path']}")
        print(f"   Size: {result['size']} bytes")
        print(f"   Modified: {result.get('modified', 'N/A')}\n")
    
    # ===========================================
    # Test 6: Security - Path traversal
    # ===========================================
    print("🔒 Test 6: Security - Path traversal attempt")
    print("-"*40)
    
    result = tool.read_file("../../etc/passwd")
    print(f"   Success: {result['success']}")
    print(f"   Error: {result.get('error', 'No error')}\n")
    
    # ===========================================
    # Test 7: Delete file
    # ===========================================
    print("🗑️ Test 7: Delete file")
    print("-"*40)
    
    result = tool.delete_file("outputs/test.txt")
    print(f"   Success: {result['success']}")
    print(f"   Path: {result.get('path', 'N/A')}\n")
    
    # ===========================================
    # Test 8: Verify deletion
    # ===========================================
    print("🔍 Test 8: Verify deletion")
    print("-"*40)
    
    result = tool.get_file_info("outputs/test.txt")
    print(f"   Exists: {result['exists']}\n")
    
    # ===========================================
    # Test 9: Workspace info
    # ===========================================
    print("📊 Test 9: Workspace info")
    print("-"*40)
    
    result = tool.get_workspace_info()
    print(f"   Workspace: {result['workspace']}")
    print(f"   Total files: {result['total_files']}")
    print(f"   Total size: {result['total_size_mb']:.2f} MB\n")
    
    # ===========================================
    # Summary
    # ===========================================
    print("="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    test_file_tools()
