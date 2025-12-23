import hyperion, time, random

# Get the parameters
snow_density = float(hyperion.args.get('snow_density', 0.3))  # 0.0 to 1.0
fall_speed = float(hyperion.args.get('fall_speed', 0.5))    # 0.1 to 2.0
twinkle_frequency = float(hyperion.args.get('twinkle_frequency', 0.1))  # 0.0 to 1.0
base_brightness = float(hyperion.args.get('base_brightness', 0.2))  # 0.0 to 1.0
snow_color = hyperion.args.get('snow_color', (200, 220, 255))  # Light blue-white
twinkle_color = hyperion.args.get('twinkle_color', (255, 255, 255))  # Bright white

# Limit update rate
min_update_interval = hyperion.lowestUpdateInterval()
update_interval = max(min_update_interval, 0.05)  # 50ms minimum

# Snowflake positions and states
snowflakes = []
led_count = hyperion.ledCount

def initialize_snowflakes():
    """Initialize snowflake positions randomly."""
    global snowflakes
    snowflakes = []
    num_snowflakes = int(snow_density * led_count)
    
    for _ in range(num_snowflakes):
        snowflakes.append({
            'position': random.uniform(0, led_count - 1),
            'speed': random.uniform(fall_speed * 0.5, fall_speed * 1.5),
            'brightness': base_brightness,
            'twinkling': False,
            'twinkle_timer': 0
        })

def update_snowflakes():
    """Update snowflake positions and states."""
    for flake in snowflakes:
        # Move snowflake down (increase position)
        flake['position'] += flake['speed']
        
        # If snowflake reaches bottom, reset to top
        if flake['position'] >= led_count:
            flake['position'] = random.uniform(-10, 0)  # Start above visible area
            flake['speed'] = random.uniform(fall_speed * 0.5, fall_speed * 1.5)
        
        # Random twinkling
        if not flake['twinkling'] and random.random() < twinkle_frequency * 0.1:
            flake['twinkling'] = True
            flake['twinkle_timer'] = random.uniform(0.1, 0.5)
        
        # Update twinkling state
        if flake['twinkling']:
            flake['twinkle_timer'] -= update_interval
            if flake['twinkle_timer'] <= 0:
                flake['twinkling'] = False

def generate_led_data():
    """Generate LED data based on current snowflake positions."""
    led_data = bytearray(led_count * 3)
    
    # Set base snow color for all LEDs (dim background)
    base_r, base_g, base_b = [int(c * base_brightness * 0.3) for c in snow_color]
    for i in range(led_count):
        led_data[i*3] = base_r
        led_data[i*3+1] = base_g
        led_data[i*3+2] = base_b
    
    # Add snowflakes
    for flake in snowflakes:
        pos = int(flake['position'])
        if 0 <= pos < led_count:
            if flake['twinkling']:
                # Twinkling snowflake (bright white)
                r, g, b = twinkle_color
            else:
                # Regular snowflake
                brightness = flake['brightness'] + random.uniform(-0.1, 0.1)
                brightness = max(0.1, min(1.0, brightness))
                r = int(snow_color[0] * brightness)
                g = int(snow_color[1] * brightness)
                b = int(snow_color[2] * brightness)
            
            # Set the LED color
            led_data[pos*3] = r
            led_data[pos*3+1] = g
            led_data[pos*3+2] = b
    
    return led_data

# Initialize snowflakes
initialize_snowflakes()

# Main snowfall loop
while not hyperion.abort():
    update_snowflakes()
    led_data = generate_led_data()
    hyperion.setColor(led_data)
    time.sleep(update_interval)
    
    # Occasionally reinitialize snowflakes for variety
    if random.random() < 0.001:  # Very rare
        initialize_snowflakes()