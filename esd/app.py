from flask import Flask, jsonify
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
import logging
from pythonjsonlogger import jsonlogger
import time
import random

app = Flask(__name__)

# ==========================================
# PART C: JSON LOGGING SETUP
# ==========================================
logger = logging.getLogger("fast-food-api")
logger.setLevel(logging.INFO)

# Output logs to a file that Filebeat can easily read
logHandler = logging.FileHandler("app-logs.json")
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# ==========================================
# PART B: PROMETHEUS METRICS SETUP
# ==========================================
# 1. Counter
ORDERS_PLACED = Counter('orders_placed_total', 'Total number of orders placed')
# 2. Gauge
ORDERS_WAITING = Gauge('orders_waiting', 'Number of orders currently being prepared')
# 3. Histogram
COOK_TIME_HIST = Histogram('cook_time_seconds', 'Time taken to prepare an order', buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 30.0])
# 4. Summary
COOK_TIME_SUM = Summary('cook_time_summary_seconds', 'Summary of cook times')

DEMO_REQUESTS = Counter('demo_requests_total', 'Test cardinality', ['request_id'])
# ==========================================
# PART A: THE FAST-FOOD API LOGIC
# ==========================================
@app.route('/order', methods=['POST'])
def place_order():
    # Generate a random ID for the structured logs
    request_id = f"ord_{random.randint(1000, 9999)}"
    logger.info("Order received", extra={"request_id": request_id, "service": "food-api", "severity": "INFO"})
    # CARDINALITY EXPERIMENT: Generate 100 unique time series instantly
    DEMO_REQUESTS.labels(request_id=request_id).inc()
    ORDERS_PLACED.inc()
    ORDERS_WAITING.inc()
    start_time = time.time()

    
    
    try:
        # Simulate the kitchen making the food
        cook_time = random.uniform(5.0, 10.0)
        time.sleep(cook_time)

        # time.sleep(random.uniform(5.0, 10.0) + 15)
        
        logger.info("Order complete", extra={"request_id": request_id, "service": "food-api", "severity": "INFO"})
        return jsonify({"status": "Order ready!", "order_id": request_id}), 200
        
    finally:
        # Stop the timer and record the metrics
        duration = time.time() - start_time
        COOK_TIME_HIST.observe(duration)
        COOK_TIME_SUM.observe(duration)
        ORDERS_WAITING.dec()

# Expose the /metrics endpoint for Prometheus to scrape
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    logger.info("Server started", extra={"service": "food-api", "severity": "INFO"})
    app.run(port=5000)