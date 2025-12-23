import hyperion, time

# Get the parameters
transition_time = float(hyperion.args.get('transition_time', 1000))/1000.0
hold_time = float(hyperion.args.get('hold_time', 3000))/1000.0
ball_size = int(hyperion.args.get('ball_size', 1))
black_size = int(hyperion.args.get('black_size', 30))
color_pairs = hyperion.args.get('color_pairs', [(255,0,0), (255,255,0), (0,0,255), (0,255,0)])

# Limit update rate
transition_time = max(hyperion.lowestUpdateInterval(), transition_time)
hold_time = max(hyperion.lowestUpdateInterval(), hold_time)

# Fixed number of steps for smooth transitions
transition_steps = 20

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors."""
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)

def generate_led_data(color1, color2, ball_size, black_size):
    """Generate LED data for a color pair."""
    led_data = bytearray()
    for _ in range(ball_size):
        led_data += bytearray(color1)
    for _ in range(black_size):
        led_data += bytearray((0, 0, 0))
    for _ in range(ball_size):
        led_data += bytearray(color2)
    for _ in range(black_size):
        led_data += bytearray((0, 0, 0))
    return led_data

# Smooth transition between color pairs via black
while not hyperion.abort():
    for i in range(0, len(color_pairs), 2):
        color1 = color_pairs[i]
        color2 = color_pairs[i+1] if (i+1) < len(color_pairs) else color_pairs[i]

        # Fade in current color pair
        for step in range(transition_steps):
            factor = step / transition_steps
            current_color1 = interpolate_color((0, 0, 0), color1, factor)
            current_color2 = interpolate_color((0, 0, 0), color2, factor)
            led_data = bytearray()
            while len(led_data) < 3 * hyperion.ledCount:
                led_data += generate_led_data(current_color1, current_color2, ball_size, black_size)
            led_data = led_data[:3 * hyperion.ledCount]
            hyperion.setColor(led_data)
            time.sleep(transition_time / transition_steps)

        # Hold current color pair
        led_data = bytearray()
        while len(led_data) < 3 * hyperion.ledCount:
            led_data += generate_led_data(color1, color2, ball_size, black_size)
        led_data = led_data[:3 * hyperion.ledCount]
        hyperion.setColor(led_data)
        time.sleep(hold_time)

        # Fade out current color pair to black
        for step in range(transition_steps):
            factor = 1 - step / transition_steps
            current_color1 = interpolate_color((0, 0, 0), color1, factor)
            current_color2 = interpolate_color((0, 0, 0), color2, factor)
            led_data = bytearray()
            while len(led_data) < 3 * hyperion.ledCount:
                led_data += generate_led_data(current_color1, current_color2, ball_size, black_size)
            led_data = led_data[:3 * hyperion.ledCount]
            hyperion.setColor(led_data)
            time.sleep(transition_time / transition_steps)
