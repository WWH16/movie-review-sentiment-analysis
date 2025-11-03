import requests

api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'


def test_tmdb_images():
    print("\n" + "=" * 60)
    print("TMDb Poster + Backdrop Test")
    print("=" * 60)

    # Test samples
    tests = [
        {'title': 'Inception', 'year': 2010, 'type': 'movie'},
        {'title': 'Breaking Bad', 'year': 2008, 'type': 'tv'},
        {'title': 'Oppenheimer', 'year': 2023, 'type': 'movie'},
    ]

    for item in tests:
        print(f"\nTesting: {item['title']} ({item['year']})")

        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/search/{item['type']}",
                params={
                    'api_key': api_key,
                    'query': item['title'],
                    'year': item['year']
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data['results']:
                    result = data['results'][0]

                    # Check poster
                    if result.get('poster_path'):
                        poster = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
                        print(f"  ✓ Poster:   {poster}")
                    else:
                        print("  ✗ Poster:   Not available")

                    # Check backdrop
                    if result.get('backdrop_path'):
                        backdrop = f"https://image.tmdb.org/t/p/w500{result['backdrop_path']}"
                        print(f"  ✓ Backdrop: {backdrop}")
                    else:
                        print("  ✗ Backdrop: Not available")
                else:
                    print("  ✗ No results found")
            else:
                print(f"  ✗ API Error: {response.status_code}")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_tmdb_images()