import argparse
import csv

import AveryLabels
from reportlab.lib.units import mm
from reportlab_qrcode import QRCodeImage
from reportlab.pdfgen import canvas


def render(c: canvas.Canvas, width: float, height: float, count: int, chips: dict):
	c.saveState()

	font_size = 6 * mm
	qr_size = 0.9
	qr_margin = 1 * mm

	position_helper = False

	if count in chips:
		chip_id = chips[count]
	else:
		chip_id = None

	if chip_id:
		qr = QRCodeImage(chip_id, size=height * qr_size)
		qr.drawOn(c, x=qr_margin, y=height * ((1 - qr_size) / 2))
		c.setFont("Courier", size=2 * mm)
		c.drawString(x=height, y=(height - 3 * mm), text=chip_id)

	c.setFont("Helvetica", size=font_size)
	c.drawString(x=height, y=(height - font_size) / 2, text=str(count))

	if position_helper:
		r = 0.1
		d = 0
		c.circle(x_cen=0 + d, y_cen=0 + d, r=r, stroke=1)
		c.circle(x_cen=width - d, y_cen=0 + d, r=r, stroke=1)
		c.circle(x_cen=0 + d, y_cen=height - d, r=r, stroke=1)
		c.circle(x_cen=width - d, y_cen=height - d, r=r, stroke=1)

	c.restoreState()


def main():
	argp = argparse.ArgumentParser(description="Print chip labels")
	argp.add_argument("-l", "--lax", action='store_true', help="Lax mode")
	argp.add_argument("-n", "--number", type=int, help="Number of labels to print", default=189)
	argp.add_argument("-o", "--offset", type=int, help="Offset for labels", default=0)
	argp.add_argument("-p", "--placement", type=int, help="Placement offset of labels", default=0)
	argp.add_argument("-f", "--filename", type=str, help="Output filename", default="chiplabels.pdf")
	# add chipfile
	argp.add_argument("-c", "--chipfile", type=str, help="Chip file", default=None)
	argp.add_argument("--delimiter", type=str, help="Delimiter for chip file", default=";")
	args = argp.parse_args()

	# open csv chipfile and read all entries race_number;chip_id to a dictionary

	if args.lax is False and args.chipfile is None:
		print("Error: Chip file is required in strict mode.")

	if args.chipfile is None:
		chips = {}
	else:
		with open(args.chipfile, mode='r') as file:
			reader = csv.reader(file, delimiter=args.delimiter)
			chips = {int(rows[1]): rows[0] for rows in reader}

	label = AveryLabels.AveryLabel(4731)

	label.open(args.filename)

	placement = args.placement

	if args.lax is False:
		for i in chips:
			label.render(lambda c, w, h: render(c, w, h, i, chips), count=1, offset=placement)
			placement = 0
	else:
		for i in range(args.offset + 1, args.offset + args.number + 1):
			label.render(lambda c, w, h: render(c, w, h, i, chips), count=1, offset=placement)
			placement = 0
	label.close()


if __name__ == "__main__":
	main()
