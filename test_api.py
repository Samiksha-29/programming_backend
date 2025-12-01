"""
Simple test script to verify API functionality
Run: python test_api.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_create_room():
    print("\n1. Testing Room Creation...")
    response = requests.post(f"{BASE_URL}/rooms")
    assert response.status_code == 200
    room_id = response.json()["roomId"]
    print(f"✓ Room created: {room_id}")
    return room_id

def test_get_room(room_id):
    print("\n2. Testing Get Room Info...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Room info: {json.dumps(data, indent=2)}")
    return data

def test_get_files(room_id):
    print("\n3. Testing Get Files...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/files")
    assert response.status_code == 200
    files = response.json()
    print(f"✓ Found {len(files)} file(s)")
    for file in files:
        print(f"  - {file['filename']} (ID: {file['id']})")
    return files

def test_create_file(room_id):
    print("\n4. Testing File Creation...")
    response = requests.post(f"{BASE_URL}/files", json={
        "filename": "test.py",
        "roomId": room_id
    })
    assert response.status_code == 200
    file_data = response.json()
    print(f"✓ File created: {file_data['filename']} (ID: {file_data['id']})")
    return file_data

def test_update_file(file_id):
    print("\n5. Testing File Update...")
    code = "def hello():\n    print('Hello from test!')\n\nhello()"
    response = requests.put(f"{BASE_URL}/files/{file_id}", json={
        "content": code
    })
    assert response.status_code == 200
    print(f"✓ File updated successfully")

def test_autocomplete():
    print("\n6. Testing Autocomplete...")
    test_cases = [
        {"code": "def ", "cursorPosition": 4, "expected": "main():"},
        {"code": "print", "cursorPosition": 5, "expected": "()"},
        {"code": "import", "cursorPosition": 6, "expected": " os"},
        {"code": "for", "cursorPosition": 3, "expected": " i in range(10):"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        response = requests.post(f"{BASE_URL}/autocomplete", json={
            "code": test["code"],
            "cursorPosition": test["cursorPosition"],
            "language": "python"
        })
        assert response.status_code == 200
        suggestion = response.json()["suggestion"]
        print(f"  {i}. '{test['code']}' → '{suggestion}'")
    
    print("✓ Autocomplete working")

def test_code_execution(room_id):
    print("\n7. Testing Code Execution...")
    code = "print('Hello World')\nprint(2 + 2)"
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/execute", json={
        "code": code
    })
    assert response.status_code == 200
    result = response.json()
    print(f"✓ Code executed:")
    print(f"  Output: {result['output']}")
    print(f"  Execution ID: {result['executionId']}")
    return result['executionId']

def test_execution_history(room_id):
    print("\n8. Testing Execution History...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/executions?limit=5")
    assert response.status_code == 200
    executions = response.json()
    print(f"✓ Found {len(executions)} execution(s)")
    for ex in executions:
        print(f"  - ID {ex['id']}: {ex['executedAt']}")

def test_active_users(room_id):
    print("\n9. Testing Active Users...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/active-users")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ Active users: {data['count']}")
    print(f"  Users: {data['activeUsers']}")

def main():
    print("=" * 60)
    print("Real-Time Pair Programming API - Test Suite")
    print("=" * 60)
    
    try:
        # Test sequence
        room_id = test_create_room()
        test_get_room(room_id)
        files = test_get_files(room_id)
        new_file = test_create_file(room_id)
        test_update_file(new_file['id'])
        test_autocomplete()
        test_code_execution(room_id)
        test_execution_history(room_id)
        test_active_users(room_id)
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print(f"\nYour test room ID: {room_id}")
        print(f"WebSocket URL: ws://localhost:8000/ws/rooms/{room_id}")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to server. Is it running?")
        print("  Start server with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
