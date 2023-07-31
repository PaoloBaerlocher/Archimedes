import png
import Acorn256

LEVEL_WIDTH = 20
LEVEL_HEIGHT = 1920

SCR_WIDTH = 244
SCR_HEIGHT = 240

def convert_level(input, output):
    img = []

    with open(input, 'rb') as f:
        for y in range(LEVEL_HEIGHT):
            row = ()
            for x in range(LEVEL_WIDTH):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                if int_val == 0 and y >= 720:
                    rgba = (0,0,0,0)		# Transparent
                else:
                    rgb = Acorn256.convert('acorn', 'rgb', int_val)
                    rgba = (rgb[0], rgb[1], rgb[2], 255)
                row = row + rgba
            img.append(row)
        
    with open(output, 'wb') as f:
        w = png.Writer(LEVEL_WIDTH, len(img), greyscale=False, alpha=True)
        w.write(f, img)

    return None

def convert_screen(input, output, width, height):
    img = []
    
    with open(input, 'rb') as f:
        for y in range(height):
            row = ()
            for x in range(width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                rgb = Acorn256.convert('acorn', 'rgb', int_val)
                rgba = (rgb[0], rgb[1], rgb[2], 255)
                row = row + rgba
            img.append(row)
 
    with open(output, 'wb') as f:
        w = png.Writer(width, len(img), greyscale=False, alpha=True)
        w.write(f, img)

    return None

def convert_shared_blocs(input, output, width, height, maskFile):

    # Load masks

    maskBlocs = []
    with open(maskFile, 'rb') as f:
        for y in range(4*20):
            row = []
            for x in range(width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                alpha = 0 if int_val == 0 else 0xFF
                row.append(alpha)
            maskBlocs.append(row)

    #

    for mask in range(0, 4):
        blocs = []

        with open(input, 'rb') as f:
            for y in range(height):
                row = ()
                for x in range(width):
                    byte_val = f.read(1)
                    int_val = int.from_bytes(byte_val)
                    rgb = Acorn256.convert('acorn', 'rgb', int_val)
                    rgba = (rgb[0], rgb[1], rgb[2], maskBlocs [(len(blocs) % 20) + mask * 20][x])
                    row = row + rgba
                if ((y >= 12844 and y <= 13323) or (y >= 14044 and y <= 14083)):
                    blocs.append(row)

        with open(output [mask], 'wb') as f:
            w = png.Writer(width, len(blocs), greyscale=False, alpha=True)
            w.write(f, blocs)

    return None

def convert_pengos(input, output, width, height):
    pengos = []

    with open(input, 'rb') as f:
        for y in range(height):
            row = ()
            for x in range(2*width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                if int_val == 0:
                    rgba = (0, 0, 0, 0)
                else:
                    rgb = Acorn256.convert('acorn', 'rgb', int_val)
                    rgba = (rgb[0], rgb[1], rgb[2], 255)
                if (int(x/4) % 2 == 0):
                    row = row + rgba
            if (y >= 14084/2) and (len(pengos) < 1680):
                pengos.append(row)

    with open(output, 'wb') as f:
        w = png.Writer(width, len(pengos), greyscale=False, alpha=True)
        w.write(f, pengos)

    return None

def convert_chars(input, output, width, height):
    blocs = []
    with open(input, 'rb') as f:
        f.read(4)  # Align with font
        for y in range(height):
            row = ()
            for x in range(width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                rgb = Acorn256.convert('acorn', 'rgb', int_val)
                rgba = (rgb[0], rgb[1], rgb[2], 255)
                row = row + rgba
            if (y >= 6525 and y <= 7400):
                blocs.append(row)

    with open(output, 'wb') as f:
        w = png.Writer(width, len(blocs), greyscale=False, alpha=True)
        w.write(f, blocs)

    return None

def convert_rocket(input, output, width, height):
    blocs = []
    with open(input, 'rb') as f:
        for y in range(height):
            row = ()
            for x in range(2*width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                if (x % 8 < 4): # Remove mask
                    if int_val == 0:
                        rgba = (0, 0, 0, 0)
                    else:
                        rgb = Acorn256.convert('acorn', 'rgb', int_val)
                        rgba = (rgb[0], rgb[1], rgb[2], 255)
                    row = row + rgba
            blocs.append(row)

    with open(output, 'wb') as f:
        w = png.Writer(width, len(blocs), greyscale=False, alpha=True)
        w.write(f, blocs)

    return None


def convert_generic(input, output, width, height, opaque):
    blocs = []
    with open(input, 'rb') as f:
        for y in range(height):
            row = ()
            for x in range(width):
                byte_val = f.read(1)
                int_val = int.from_bytes(byte_val)
                if not opaque and int_val == 0:
                    rgba = (0, 0, 0, 0)
                else:
                    rgb = Acorn256.convert('acorn', 'rgb', int_val)
                    rgba = (rgb[0], rgb[1], rgb[2], 255)
                row = row + rgba
            blocs.append(row)

    with open(output, 'wb') as f:
        w = png.Writer(width, len(blocs), greyscale=False, alpha=True)
        w.write(f, blocs)

    return None

# Main

convert_level('Levels/LEVEL1', 'level1.png')
convert_level('Levels/LEVEL2', 'level2.png')
convert_level('Levels/LEVEL3', 'level3.png')
convert_level('Levels/LEVEL4', 'level4.png')
convert_level('Levels/LEVEL5', 'level5.png')

convert_screen('Screens/ICE_SCR',    'scr1.png', SCR_WIDTH, SCR_HEIGHT)
convert_screen('Screens/ESA_SCR',    'scr2.png', SCR_WIDTH, SCR_HEIGHT)
convert_screen('Screens/SPACE_SCR',  'scr3.png', SCR_WIDTH, SCR_HEIGHT)
convert_screen('Screens/JUNGLE_SCR', 'scr4.png', SCR_WIDTH, SCR_HEIGHT)
convert_screen('Screens/ORDI_SCR',   'scr5.png', SCR_WIDTH, SCR_HEIGHT)

convert_screen('BORDER', 'border.png', 320, 256)
convert_shared_blocs('POIZ_cde', ['sharedBlocs0.png', 'sharedBlocs1.png', 'sharedBlocs2.png', 'sharedBlocs3.png'], 20, 16384, 'varius/MASKCRASH')
convert_pengos('POIZ_cde', 'pengos.png', 20, 16384)
convert_chars('POIZ_cde', 'chars.png', 12, 8192)
convert_rocket('varius/ROCKET', 'rocket.png', 40, 174)
convert_generic('varius/PLAQU_SPR', 'plaqu.png', 60, 40, True)
convert_generic('varius/ARROWS', 'arrows.png', 20, 160, False)
