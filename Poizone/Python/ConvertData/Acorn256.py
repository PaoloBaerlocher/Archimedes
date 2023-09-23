#!/usr/bin/python3
"""
This code converts colors between RGB256, HTML, HSV and ACORN256 / ACORN16.

ACORN256 / ACORN16 default color palettes, which were implemented in
'Acorn Archimedes' computers.
Because obviously there are no complete match between 8-bit and 24-bit
palettes, some of the RGB / HTML / HSV values provided will return None.

convert([input_format], [output_format], [value], [optional: palette])
	input_format, output_format - any of: 'hsv', 'rgb', 'acorn', 'html'
	value - must match the input format conventions, '#FFFFFF' for html, etc.
	palette - 'acorn16' or 'acorn256'

Examples.

From interpreter / script:
>>>acorn256.convert('acorn', 'html', 42)
'#226666'

From bash console:
$ python3 acorn256.py rgb acorn '(255, 255, 255)'
255

$ python3 acorn256.py rgb acorn '(255, 255, 255)' acorn16
0

"""

# Acorn16 | HTML | RGB256 | HSV color mapping table

TABLE16 = (
    (0, "#FFFFFF", (255, 255, 255), (0, 0, 100)),
    (1, "#DDDDDD", (221, 221, 221), (0, 0, 86)),
    (2, "#BBBBBB", (187, 187, 187), (0, 0, 73)),
    (3, "#999999", (153, 153, 153), (0, 0, 60)),
    (4, "#777777", (119, 119, 119), (0, 0, 46)),
    (5, "#555555", (85, 85, 85), (0, 0, 33)),
    (6, "#333333", (51, 51, 51), (0, 0, 20)),
    (7, "#000000", (0, 0, 0), (0, 0, 0)),
    (8, "#004499", (0, 68, 153), (312, 100, 60)),
    (9, "#EEEE00", (238, 238, 0), (60, 100, 93)),
    (10, "#00CC00", (0, 204, 0), (120, 100, 80)),
    (11, "#DD0000", (221, 0, 0), (0, 100, 86)),
    (12, "#EEEEBB", (238, 238, 187), (60, 21, 93)),
    (13, "#558800", (85, 136, 0), (82, 100, 53)),
    (14, "#FFBB00", (255, 187, 0), (44, 100, 100)),
    (15, "#00BBFF", (0, 187, 255), (196, 100, 100)),
)

# Acorn256 | HTML | RGB256 | HSV color mapping table

TABLE256 = (
    (0, "#000000", (0, 0, 0), (0, 0, 0)),
    (1, "#111111", (17, 17, 17), (0, 0, 6)),
    (2, "#222222", (34, 34, 34), (0, 0, 13)),
    (3, "#333333", (51, 51, 51), (0, 0, 20)),
    (4, "#440000", (68, 0, 0), (0, 100, 26)),
    (5, "#551111", (85, 17, 17), (0, 80, 33)),
    (6, "#662222", (102, 34, 34), (0, 66, 40)),
    (7, "#773333", (119, 51, 51), (0, 57, 46)),
    (8, "#000044", (0, 0, 68), (240, 100, 26)),
    (9, "#111155", (17, 17, 85), (240, 80, 33)),
    (10, "#222277", (34, 34, 102), (240, 66, 40)),
    (11, "#333377", (51, 51, 119), (240, 57, 46)),
    (12, "#440044", (68, 0, 68), (300, 100, 26)),
    (13, "#551155", (85, 17, 85), (300, 80, 33)),
    (14, "#662266", (102, 34, 102), (300, 66, 40)),
    (15, "#773377", (119, 51, 119), (300, 57, 46)),
    (16, "#880000", (136, 0, 0), (0, 100, 53)),
    (17, "#991111", (153, 17, 17), (0, 88, 60)),
    (18, "#AA2222", (170, 34, 34), (0, 80, 66)),
    (19, "#BB3333", (187, 51, 51), (0, 72, 73)),
    (20, "#CC0000", (204, 0, 0), (0, 100, 80)),
    (21, "#DD1111", (221, 17, 17), (0, 92, 86)),
    (22, "#EE2222", (238, 34, 34), (0, 85, 93)),
    (23, "#FF3333", (255, 51, 51), (0, 80, 100)),
    (24, "#880044", (136, 0, 68), (330, 100, 53)),
    (25, "#991155", (153, 17, 85), (330, 88, 60)),
    (26, "#AA2266", (170, 34, 102), (330, 80, 66)),
    (27, "#BB3377", (187, 51, 119), (330, 72, 73)),
    (28, "#CC0044", (204, 0, 68), (340, 100, 80)),
    (29, "#DD1155", (221, 17, 85), (340, 92, 86)),
    (30, "#EE2266", (238, 34, 102), (340, 85, 93)),
    (31, "#FF3377", (255, 51, 119), (340, 80, 100)),
    (32, "#004400", (0, 68, 0), (120, 100, 26)),
    (33, "#115511", (17, 85, 17), (120, 80, 33)),
    (34, "#226622", (34, 102, 34), (120, 66, 40)),
    (35, "#337733", (51, 119, 51), (120, 57, 46)),
    (36, "#444400", (68, 68, 0), (60, 100, 26)),
    (37, "#555511", (85, 85, 17), (60, 80, 33)),
    (38, "#666622", (102, 102, 34), (60, 66, 40)),
    (39, "#777733", (119, 119, 51), (60, 57, 46)),
    (40, "#004444", (0, 68, 68), (180, 100, 26)),
    (41, "#115555", (17, 85, 85), (180, 80, 33)),
    (42, "#226666", (34, 102, 102), (180, 66, 40)),
    (43, "#337777", (51, 119, 119), (180, 57, 46)),
    (44, "#444444", (68, 68, 68), (0, 0, 26)),
    (45, "#555555", (85, 85, 85), (0, 0, 33)),
    (46, "#666666", (102, 102, 102), (0, 0, 40)),
    (47, "#777777", (119, 119, 119), (0, 0, 46)),
    (48, "#884400", (136, 68, 0), (30, 100, 53)),
    (49, "#995511", (153, 85, 17), (30, 88, 60)),
    (50, "#AA6622", (170, 102, 34), (30, 80, 66)),
    (51, "#BB7733", (187, 119, 51), (30, 72, 73)),
    (52, "#CC4400", (204, 68, 0), (19, 100, 80)),
    (53, "#DD5511", (221, 85, 17), (19, 92, 86)),
    (54, "#EE6622", (238, 102, 34), (19, 85, 93)),
    (55, "#FF7733", (255, 119, 51), (19, 80, 100)),
    (56, "#884444", (136, 68, 68), (0, 50, 53)),
    (57, "#995555", (153, 85, 85), (0, 44, 60)),
    (58, "#AA6666", (170, 102, 102), (0, 40, 66)),
    (59, "#BB7777", (187, 119, 119), (0, 36, 73)),
    (60, "#CC4444", (204, 68, 68), (0, 66, 80)),
    (61, "#DD5555", (221, 85, 85), (0, 61, 86)),
    (62, "#EE6666", (238, 102, 102), (0, 57, 93)),
    (63, "#FF7777", (255, 119, 119), (0, 53, 100)),
    (64, "#008800", (0, 136, 0), (120, 100, 53)),
    (65, "#119911", (17, 153, 17), (120, 88, 60)),
    (66, "#22AA22", (34, 170, 34), (120, 80, 66)),
    (67, "#33BB33", (51, 187, 51), (120, 72, 73)),
    (68, "#448800", (68, 136, 0), (90, 100, 53)),
    (69, "#559911", (85, 153, 17), (90, 88, 60)),
    (70, "#66AA22", (102, 170, 34), (90, 80, 66)),
    (71, "#77BB33", (119, 187, 51), (90, 72, 73)),
    (72, "#008844", (0, 136, 68), (150, 100, 53)),
    (73, "#119955", (17, 153, 85), (150, 88, 60)),
    (74, "#22AA66", (34, 170, 102), (150, 80, 66)),
    (75, "#33BB77", (51, 187, 119), (150, 72, 73)),
    (76, "#448844", (68, 136, 68), (120, 50, 53)),
    (77, "#559955", (85, 153, 85), (120, 44, 60)),
    (78, "#66AA66", (102, 170, 102), (120, 40, 66)),
    (79, "#77BB77", (119, 187, 119), (120, 36, 73)),
    (80, "#888800", (136, 136, 0), (60, 100, 53)),
    (81, "#999911", (153, 153, 17), (60, 88, 60)),
    (82, "#AAAA22", (170, 170, 34), (60, 80, 66)),
    (83, "#BBBB33", (187, 187, 51), (60, 72, 73)),
    (84, "#CC8800", (204, 136, 0), (40, 100, 80)),
    (85, "#DD9911", (221, 153, 17), (40, 92, 86)),
    (86, "#EEAA22", (238, 170, 34), (40, 85, 93)),
    (87, "#FFBB33", (255, 187, 51), (40, 80, 100)),
    (88, "#888844", (136, 136, 68), (60, 50, 53)),
    (89, "#999955", (153, 153, 85), (60, 44, 60)),
    (90, "#AAAA66", (170, 170, 102), (60, 40, 66)),
    (91, "#BBBB77", (187, 187, 119), (60, 36, 73)),
    (92, "#CC9944", (204, 136, 68), (30, 66, 80)),
    (93, "#DD9955", (221, 153, 85), (30, 61, 86)),
    (94, "#EEAA66", (238, 170, 102), (30, 57, 93)),
    (95, "#FFBB77", (225, 187, 119), (30, 53, 100)),
    (96, "#00CC00", (0, 204, 0), (120, 100, 80)),
    (97, "#11DD11", (17, 221, 17), (120, 92, 86)),
    (98, "#22EE22", (34, 238, 34), (120, 85, 93)),
    (99, "#33FF33", (51, 255, 51), (120, 60, 100)),
    (100, "#44CC00", (68, 204, 0), (100, 100, 80)),
    (101, "#55DD11", (85, 221, 17), (100, 92, 86)),
    (102, "#66EE22", (102, 238, 34), (100, 85, 93)),
    (103, "#77FF33", (119, 255, 51), (100, 80, 100)),
    (104, "#00CC44", (0, 204, 68), (140, 100, 80)),
    (105, "#11DD55", (17, 221, 85), (140, 92, 86)),
    (106, "#22EE66", (34, 238, 102), (140, 85, 93)),
    (107, "#33FF77", (51, 255, 119), (140, 80, 100)),
    (108, "#44CC44", (68, 204, 68), (120, 66, 80)),
    (109, "#55DD55", (85, 221, 85), (120, 61, 86)),
    (110, "#66EE66", (102, 238, 102), (120, 57, 93)),
    (111, "#77FF77", (119, 255, 119), (120, 53, 100)),
    (112, "#88CC00", (136, 204, 0), (80, 100, 80)),
    (113, "#99DD11", (153, 221, 17), (80, 92, 86)),
    (114, "#AAEE22", (170, 238, 34), (80, 85, 93)),
    (115, "#BBFF33", (187, 225, 51), (80, 80, 100)),
    (116, "#CCCC00", (204, 204, 0), (60, 100, 80)),
    (117, "#DDDD11", (221, 221, 17), (60, 92, 86)),
    (118, "#EEEE22", (238, 238, 34), (60, 85, 93)),
    (119, "#FFFF33", (255, 255, 51), (60, 80, 100)),
    (120, "#88CC44", (136, 204, 68), (90, 66, 80)),
    (121, "#99DD55", (153, 221, 85), (90, 61, 86)),
    (122, "#AAEE66", (170, 238, 102), (90, 57, 93)),
    (123, "#BBFF77", (187, 255, 119), (90, 53, 100)),
    (124, "#CCCC44", (204, 204, 68), (60, 66, 60)),
    (125, "#DDDD55", (221, 221, 85), (60, 61, 86)),
    (126, "#EEEE66", (238, 238, 102), (60, 57, 93)),
    (127, "#FFFF77", (255, 255, 119), (60, 53, 100)),
    (128, "#000088", (0, 0, 136), (240, 100, 53)),
    (129, "#111199", (17, 17, 153), (240, 88, 60)),
    (130, "#2222AA", (34, 34, 170), (240, 80, 66)),
    (131, "#3333BB", (51, 51, 187), (240, 72, 73)),
    (132, "#440088", (68, 0, 136), (270, 100, 53)),
    (133, "#551199", (85, 17, 153), (270, 88, 60)),
    (134, "#6622AA", (102, 34, 170), (270, 80, 66)),
    (135, "#7733BB", (119, 51, 187), (270, 72, 73)),
    (136, "#0000CC", (0, 0, 204), (240, 100, 80)),
    (137, "#1111DD", (17, 17, 221), (240, 92, 86)),
    (138, "#2222EE", (34, 34, 238), (240, 85, 93)),
    (139, "#3333FF", (51, 51, 255), (240, 80, 100)),
    (140, "#4400CC", (68, 0, 204), (260, 100, 80)),
    (141, "#5511DD", (85, 17, 221), (260, 92, 86)),
    (142, "#6622EE", (102, 34, 238), (260, 85, 93)),
    (143, "#7733FF", (119, 51, 255), (260, 80, 100)),
    (144, "#880088", (136, 0, 136), (300, 100, 53)),
    (145, "#991199", (153, 17, 153), (300, 88, 60)),
    (146, "#AA22AA", (170, 34, 170), (300, 80, 66)),
    (147, "#BB33BB", (187, 51, 187), (300, 72, 73)),
    (148, "#CC0088", (204, 0, 136), (320, 100, 80)),
    (149, "#DD1199", (221, 17, 153), (320, 92, 86)),
    (150, "#EE22AA", (238, 34, 170), (320, 85, 93)),
    (151, "#FF33BB", (255, 51, 187), (320, 80, 100)),
    (152, "#8800CC", (136, 0, 204), (280, 100, 80)),
    (153, "#9911DD", (153, 17, 221), (280, 92, 86)),
    (154, "#AA22EE", (170, 34, 238), (280, 85, 93)),
    (155, "#BB33FF", (187, 51, 255), (280, 80, 100)),
    (156, "#CC00CC", (204, 0, 204), (300, 100, 80)),
    (157, "#DD11DD", (221, 17, 221), (300, 92, 86)),
    (158, "#EE22EE", (238, 34, 238), (300, 85, 93)),
    (159, "#FF33FF", (225, 51, 225), (300, 80, 100)),
    (160, "#004488", (0, 68, 136), (210, 100, 53)),
    (161, "#115599", (17, 85, 153), (210, 88, 60)),
    (162, "#2266AA", (34, 102, 170), (210, 80, 66)),
    (163, "#3377BB", (51, 119, 187), (210, 72, 73)),
    (164, "#444488", (68, 68, 136), (240, 50, 53)),
    (165, "#555599", (85, 85, 153), (240, 44, 60)),
    (166, "#6666AA", (102, 102, 170), (240, 40, 66)),
    (167, "#7777BB", (119, 119, 187), (240, 36, 73)),
    (168, "#0044CC", (0, 68, 204), (220, 100, 80)),
    (169, "#1155DD", (17, 85, 221), (220, 92, 86)),
    (170, "#2266EE", (34, 102, 238), (220, 85, 93)),
    (171, "#3377FF", (51, 119, 225), (220, 80, 100)),
    (172, "#4444CC", (68, 68, 204), (240, 66, 80)),
    (173, "#5555DD", (85, 85, 221), (240, 61, 86)),
    (174, "#6666EE", (102, 102, 238), (240, 57, 93)),
    (175, "#7777FF", (119, 119, 255), (240, 53, 100)),
    (176, "#884488", (136, 68, 136), (300, 50, 53)),
    (177, "#995599", (153, 85, 153), (300, 44, 60)),
    (178, "#AA66AA", (170, 102, 170), (300, 40, 66)),
    (179, "#BB77BB", (187, 119, 187), (300, 36, 73)),
    (180, "#CC4488", (204, 68, 136), (330, 66, 80)),
    (181, "#DD5599", (221, 85, 153), (330, 61, 86)),
    (182, "#EE66AA", (238, 102, 170), (330, 57, 93)),
    (183, "#FF77BB", (255, 119, 187), (330, 53, 100)),
    (184, "#8844CC", (136, 68, 204), (270, 66, 80)),
    (185, "#9955DD", (153, 85, 221), (270, 61, 86)),
    (186, "#AA66EE", (170, 102, 238), (270, 57, 93)),
    (187, "#BB77FF", (187, 119, 255), (270, 53, 100)),
    (188, "#CC44CC", (204, 68, 204), (300, 66, 80)),
    (189, "#DD55DD", (221, 85, 221), (300, 61, 86)),
    (190, "#EE66EE", (238, 102, 238), (300, 57, 93)),
    (191, "#FF77FF", (255, 119, 255), (300, 53, 100)),
    (192, "#008888", (0, 136, 136), (180, 100, 53)),
    (193, "#119999", (17, 153, 153), (180, 88, 60)),
    (194, "#22AAAA", (34, 170, 170), (180, 80, 66)),
    (195, "#33BBBB", (51, 187, 187), (180, 72, 73)),
    (196, "#448888", (68, 136, 136), (180, 50, 53)),
    (197, "#559999", (85, 153, 153), (180, 44, 60)),
    (198, "#66AAAA", (102, 170, 170), (180, 40, 66)),
    (199, "#77BBBB", (119, 187, 187), (180, 36, 73)),
    (200, "#0088CC", (0, 136, 204), (200, 100, 80)),
    (201, "#1199DD", (17, 153, 221), (200, 92, 86)),
    (202, "#22AAEE", (34, 170, 238), (200, 65, 93)),
    (203, "#33AAFF", (51, 170, 255), (200, 80, 100)),
    (204, "#4488CC", (68, 136, 204), (210, 66, 80)),
    (205, "#5599DD", (85, 153, 221), (210, 61, 86)),
    (206, "#66AAEE", (102, 170, 238), (210, 57, 93)),
    (207, "#77BBFF", (119, 187, 255), (210, 53, 100)),
    (208, "#888888", (136, 136, 136), (0, 0, 53)),
    (209, "#999999", (153, 153, 153), (0, 0, 60)),
    (210, "#AAAAAA", (170, 170, 170), (0, 0, 66)),
    (211, "#BBBBBB", (187, 187, 187), (0, 0, 73)),
    (212, "#CC8888", (204, 136, 136), (0, 33, 80)),
    (213, "#DD9999", (221, 153, 153), (0, 30, 86)),
    (214, "#EEAAAA", (238, 170, 170), (0, 28, 93)),
    (215, "#FFBBBB", (255, 187, 187), (0, 26, 100)),
    (216, "#8888CC", (136, 136, 204), (240, 33, 80)),
    (217, "#9999DD", (153, 153, 221), (240, 30, 86)),
    (218, "#AAAAEE", (170, 170, 238), (240, 28, 93)),
    (219, "#BBBBFF", (187, 187, 255), (240, 26, 100)),
    (220, "#CC88CC", (204, 136, 204), (300, 33, 80)),
    (221, "#DD99DD", (221, 153, 221), (300, 30, 86)),
    (222, "#EEAAEE", (238, 170, 238), (300, 28, 93)),
    (223, "#FFBBFF", (255, 187, 255), (300, 26, 100)),
    (224, "#00CC88", (0, 204, 136), (160, 100, 80)),
    (225, "#11DD99", (17, 221, 153), (160, 92, 96)),
    (226, "#22EEAA", (34, 238, 170), (160, 85, 93)),
    (227, "#33FFBB", (51, 255, 187), (160, 80, 100)),
    (228, "#44CC88", (68, 204, 136), (150, 66, 80)),
    (229, "#55DD99", (85, 221, 153), (150, 61, 86)),
    (230, "#66EEAA", (102, 238, 170), (150, 57, 93)),
    (231, "#77FFBB", (119, 255, 187), (150, 53, 100)),
    (232, "#00CCCC", (0, 204, 204), (180, 100, 80)),
    (233, "#11DDDD", (17, 221, 221), (180, 92, 86)),
    (234, "#22DDDD", (34, 238, 238), (180, 85, 93)),
    (235, "#33FFFF", (51, 255, 255), (180, 80, 100)),
    (236, "#44CCCC", (68, 204, 204), (180, 66, 80)),
    (237, "#55DDDD", (85, 221, 221), (180, 61, 86)),
    (238, "#66EEEE", (102, 238, 238), (180, 57, 93)),
    (239, "#77FFFF", (119, 255, 255), (180, 53, 100)),
    (240, "#88CC88", (136, 204, 136), (120, 33, 80)),
    (241, "#99DD99", (153, 221, 153), (120, 30, 86)),
    (242, "#AAEEAA", (170, 238, 170), (120, 28, 93)),
    (243, "#BBFFBB", (187, 255, 187), (120, 26, 100)),
    (244, "#CCCC88", (204, 204, 136), (60, 33, 80)),
    (245, "#DDDD99", (221, 221, 153), (60, 30, 86)),
    (246, "#EEEEAA", (238, 238, 170), (60, 28, 93)),
    (247, "#FFFFBB", (255, 255, 187), (60, 26, 100)),
    (248, "#88CCCC", (136, 204, 204), (180, 33, 80)),
    (249, "#99DDDD", (153, 221, 221), (180, 30, 86)),
    (250, "#AAEEEE", (170, 238, 238), (180, 28, 93)),
    (251, "#BBFFFF", (187, 255, 255), (160, 26, 100)),
    (252, "#CCCCCC", (204, 204, 204), (0, 0, 80)),
    (253, "#DDDDDD", (221, 221, 221), (0, 0, 86)),
    (254, "#EEEEEE", (238, 238, 238), (0, 0, 93)),
    (255, "#FFFFFF", (255, 255, 255), (0, 0, 100)),
)

FORMATS = ('acorn', 'html', 'rgb', 'hsv')


def convert_user_input(*args):
    """
    This function converts user input to a valid format and
    calls to a `acorn256.convert` function and returns its result.
    If user input cannot be validated, it will rise a ValueError.
    args should contain at least three values:
        input format, output format and value to be converted
    the fourth argument provided may be a palette type: acorn16 | acorn256
    """

    try:
        input_format, output_format, value = args[:3]
    except ValueError:
        raise ValueError("Not enough arguments, "
            "at least input format, output format and value "
            "must be provided")
    try:
        palette = args[3]
    except IndexError:
        palette = 'acorn256'

    input_format = input_format.lower()
    output_format = output_format.lower()
    palette = palette.lower()
    value = value.lower()

    if palette == 'acorn16':
        palette = TABLE16
    elif palette == 'acorn256' or palette == 'acorn':
        palette = TABLE256
    else:
        raise ValueError("palette should be either acorn16 or acorn256")

    if input_format not in FORMATS or output_format not in FORMATS:
        raise ValueError("formats should be one of these: %s" % str(FORMATS))

    if input_format == 'acorn':
        value = int(value)
        if value < 0 or value >= len(palette):
            raise ValueError("requested value outside of the palette range")
    elif input_format in ('rgb', 'hsv'):
        value = value.strip()
        value = value[1:-1].split(',')
        value = tuple((int(v.strip()) for v in value))
        for v in value:
            if v < 0 or v > 255:
                raise ValueError("%s must be provided in 8bit uint format" %
                    input_format)
    elif input_format == 'html':
        if len(value) != 7:
            raise ValueError("html color should be provided"
                "in #XXXXXX format")
    return convert(input_format, output_format, value, palette)


def convert(input_format, output_format, value, palette=TABLE256):
    """
    This function actually searches a palette for matching values.
    It doesn't validate arguments.
    You should use `acorn256.convert_user_input` in case of user input.
    """

    in_id = FORMATS.index(input_format)
    out_id = FORMATS.index(output_format)

    for values in palette:
        if values[in_id] == value:
            return values[out_id]
    else:
        return None


if __name__ == '__main__':
    # to be used from the terminal
    import sys

    try:
        sys.stdout.write('%s\n' % convert_user_input(*sys.argv[1:]))
    except ValueError as e:
        print(str(e))

    sys.exit(0)
