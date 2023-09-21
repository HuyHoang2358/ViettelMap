import requests, math, json
import time
import threading
from tqdm import tqdm

def calculate_time_left(start_time, current_index, total):
    elapsed_time = time.time() - start_time
    average_time_per_request = elapsed_time / (current_index + 1)
    remaining_requests = total - current_index - 1
    time_left = remaining_requests * average_time_per_request
    return time_left


def generate_points_around_center(center_lat, center_lon, radius):
    points = []
    for r in range(1,radius,20):
        n_point = int(3.14*2*r/36)
        for i in range(n_point):
            angle = 2 * math.pi * i / n_point
            dx = r * math.cos(angle)
            dy = r * math.sin(angle)
            
            new_lat = center_lat + (180 / math.pi) * (dy / 6371000)
            new_lon = center_lon + (180 / math.pi) * (dx / (6371000 * math.cos(center_lat * math.pi / 180)))
            
            points.append((new_lat, new_lon))
    return points

def generate_key_points_around_center(center_lat, center_lon, radius):
    points = []
    for r in range(1,radius,100):
        n_point = int(3.14*2*r/120)
        for i in range(n_point):
            angle = 2 * math.pi * i / n_point
            dx = r * math.cos(angle)
            dy = r * math.sin(angle)
            
            new_lat = center_lat + (180 / math.pi) * (dy / 6371000)
            new_lon = center_lon + (180 / math.pi) * (dx / (6371000 * math.cos(center_lat * math.pi / 180)))
            
            pps = generate_points_around_center(new_lat, new_lon,80)
            points = points + pps
    return points

def draw_points_to_json_file(points, center_point, radius, json_file):
    data = {}
    data["center_point"] = center_point,
    data["radius"] = radius,
    data["num_points"] = len(points)
    data["points"] = []
   
    for p in points:
        data["points"].append({
            "lat": p[0],
            "lon": p[1]
        })
    
    with open(json_file, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def send_request(points, thread_index):
    data = []
    LIMIT_REQUEST = 100
    title = f"{len(points)} || Thread - {thread_index}: "
    with tqdm(total=len(points), desc= title, bar_format="{l_bar}{bar}        [ time left: {remaining} ]") as pbar:
        for index,point in enumerate(points): 
            if not(index % LIMIT_REQUEST):
                time.sleep(1)
            else:
                try:
                    api_url = f"{URL}pt={point[0]},%20{point[1]}&k=4474ace29cd4d4fa14847303d2a6d6f0"
                    response = requests.get(api_url)
                    new_address = json.loads(response.text)["data"]
                    #print(new_address)
                    data_item = {
                        "lat": str(point[0]),
                        "lon": str(point[1]),
                        "address": new_address
                    }
                    data.append(data_item)
                except:
                    pass
            pbar.update(1)
    return data


######################################################################## MAIN ##########################################################################################
def main(center_point, radius):
    points = generate_key_points_around_center(center_point["lat"], center_point["lon"], radius)
    draw_points_to_json_file(points, center_point, radius, POINTS_JSON)
    num_threads = 10
    threads = []
    num_requests_each_thread = len(points)//num_threads
    results = []
    start_time = time.time()

    for i in range(num_threads):
        
        thread = threading.Thread(target=lambda: results.append(send_request(points[i*num_requests_each_thread : min((i+1)*num_requests_each_thread,len(points))],i+1)), name=f'Thread-{i+1}')
        #print(thread)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

    ans = []
    add = []
    for r in results:
        for i in r: 
            if not(i["address"] in add):
                ans.append(i)
                add.append(i["address"])

    print(f"Total points: {len(points)}")
    print(f"Total results: {len(ans)}")
    print(f"Total time: { time.time() - start_time}")


   

    with open("data/data.json", 'w', encoding="utf-8") as f:
        json.dump(ans, f, ensure_ascii=False, indent=4)
    
########################################################################################################################################################################
CENTER_POINT = {
    "lat": 20.858822,
    "lon": 106.688789,
}
RADIUS = 1000  # m
DATA_FOLDER = "data/"
POINTS_JSON = DATA_FOLDER + "points.json"
URL = "https://api-maps.viettel.vn/gateway/placeapi/v2-old/place-api/VTMapService/geoprocessing?f=getaddr&"


main(CENTER_POINT, RADIUS)


########################################################################################################################################################################





