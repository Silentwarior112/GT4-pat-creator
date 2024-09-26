# GT4-pat-creator
Python scripts to automate generation of GT4 color patch files from scratch without an existing pat file.
While the time and effort required is rather high, this allows for custom recoloring of any
car in Gran Turismo 4 and to a slightly lesser extent any GT game that uses the Tex1 format.

-- GT4 Color patch generator script --
Creates GT4 pat files based on the difference between two MDLS models.

-- Tex1 to PNG byte map script --
1. Exports Tex1 palette / color data to PNG and generates a mask with it
to help rule out irrelevant pixels.

2. Imports PNG pixels into a provided Tex1. Rather than an outright conversion,
   this simply replaces the bytes within the same range it would extract from.
   This preserves all of the header data.

Usage:
1. Split the model file using the Model extractor & rebuilder script,
at least extract the MainModel.

2. Extract the necessary Tex1 file(s) inside the MainModel.bin.
	- Many cars have multiple Tex1 files inside their models but
	in general there should only be one that is relevant which is
	going to be the "big" Tex1, it should be the first one packed 
	into the model. Look at the byte count value inside the Tex1
	binary data to determine if it's the "big" one.
	To find the Tex1, use a hex editor and search for string: Tex1
	Once found, highlight the first few bytes of it to start the selection
	and then check to byte count value at 0xC through 0xF to know how much
	to select. HxD will show your highlighted length in the bottom right.

	Once the bytes are copied, paste them into a new binary file in the hex
	editor and save as a separate file. The file extension can simply be .bin.
	
3. Before continuing, make duplicates of the MainModel.bin file and the Tex1 file your
	just saved. Rename the filenames and add something such as _original to make clear which
	file is which.
	
4. Use the Tex1 to PNG Byte map script to extract the relevant binary data
	from the Tex1 and import that data into a PNG.
	- The script will output the PNG, and a mask PNG.
	The mask PNG recolors every pixel depending on certain criteria
	to determine which pixels should be ruled out and which to focus on.
	In the mask, there are 4 categories of pixels:
	Red: Has 0 opacity. Mostly ignore except for pixels with relevant RGB values adjacent to relevant pixels.
	Green: Invalid
	Blue: Valid Colors
	Differenced: Valid shades
	
5. Open an image editor and open the two PNG files. Paint.net is recommended as it preserves all 4 channel values of pixels
regardless of the channel values.

Use the mask file to get an idea of which pixels
	to consider. The most important thing to look for are single-pixel height gradient strips.
	If the color of those gradients appears relevant, it's nearly a guarantee that it is.
	
	Techniques:
	1. Magic Wand: Global flood mode with ~20% or less tolerance.
	Select a relevant pixel and allow the magic wand to select
	pixels for you. This could give a starting point that you can
	use for later passes.
	
	2. "Big square overwrite": When trying to pinpoint a certain section
	of the car you need to find, you can overwrite a chunk of the entire
	PNG with a single color. For example, the top half, quarter, eighth, etc.
	You can check if the desired part of the model
	changed to that color. If it didn't, go back and move the square to the next
	section and try again until the part changes. When it does, continue to shrink the
	square until you are able to pinpoint the pixels responsible.
	
	3. Remember, this is only to generate the target offsets needed to make the color patch.
	Do not waste effort trying to recolor the car in any kind of 'proper' way just yet.
	Change the pixels to anything that would be obvious and use basic effects.
	
6. Once the PNG is edited, use the Tex1 to PNG Byte map script again and this time import
	the PNG into the Tex1.
	Select the Tex1 file, then select the modified PNG.
	Save the output file as a separate file, name it something such as MainModelTex1_test.

7. Inject the Tex1 into the MainModel (MDLS). HxD provides quick injection and re-injection
into the MDLS as files update with HxD in real time.
	- Open the MainModel MDLS file, and also open the Tex1 to inject in hex editor.
	Search for the Tex1 inside the MDLS just like from earlier and highlight the entire Tex1.
	Tab over to the Tex1 file you want to inject, and Ctrl+A to highlight all, copy (Ctrl+C),
	then tab back over to the MDLS and paste (Ctrl+V) over the highlighted Tex1.
	Save as MainModel.bin
	
8. Use the Model extractor & rebuilder script to rebuild the model with the new MainModel.bin.
	- View the model in one of the game's menus such as a dealership and inspect it.
	To refresh the model, simply hover the game's cursor over to another car and then back again.
	You'll be bouncing back to step 5 multiple times until all of the colors of the model you want
	to get picked up by the pat file generator have been found in the PNG.
	
9. Once you have found every relevant pixel in the PNG, you can inject your final iteration of the
	Tex1 into the MainModel.bin and optionally also change all of the material values in it
	(in order for the script to pick them up for editing later in the color patch) to begin.
	The final iteration should have every relevant pixel changed to something that
	changes each channel, or at least the Red channel. The pat generator script will round
	the patch size up to the next multiple of 4 bytes so that it always picks up the full 4
	bytes needed to fully define colors.
	
	You should have the modified MDLS / MainModel.bin and the original MDLS you duplicated from earlier.
	Use the pat file generator script to create a GT4 pat file based on the difference between
	the two files. As the script will suggest, input the modified file first, then the original file second
	to make the script populate the color patch with the proper color data.
	This will generate the patch file with one variaion populated into it.

10. Use the color adder script to add at least one variation to the color patch so that you can test
	it out.

11. Use the color editor script to export the patch data to a PNG.
	From here the process is exactly the same as already mentioned
	with color patch editing. Make a new PNG strip and import it into
	slot 2, save the file, rebuild the model with the new MainModelColorPatch.pat
	and add an entry into the spec database and test your model.
	
