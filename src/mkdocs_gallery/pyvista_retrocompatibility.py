"""Retrocompatibility for pyvista generate_images function.

If the actual version of pyvista does not have the generate_images function,
this module will provide a copy of the function.

(Should be obsolete in next pyvista release.)
"""

try:
    from pyvista.plotting.utilities.sphinx_gallery import generate_images

except (ModuleNotFoundError, ImportError):
    # If generate_images is not available, a very ugly copy/paste of the function is done here
    # this will be obsolete in next pyvista release
    import pyvista
    import shutil
    import os
    from typing import Iterator, List

    def _process_events_before_scraping(plotter):
        """Process events such as changing the camera or an object before scraping."""
        if plotter.iren is not None and plotter.iren.initialized:
            # check for pyvistaqt app which can be specifically bound to pyvista plotter
            # objects in order to interact with qt, then process the events from qt
            if hasattr(plotter, "app") and plotter.app is not None:
                plotter.app.processEvents()
            plotter.update()

    def generate_images(image_path_iterator: Iterator[str], dynamic: bool = False) -> List[str]:
        """Generate images from the current plotters.

        The file names are taken from the ``image_path_iterator`` iterator.

        A gif will be created if a plotter has a ``_gif_filename`` attribute.
        Otherwise, depending on the value of ``dynamic``, either a ``.png`` static image
        or a ``.vtksz`` file will be created.

        Parameters
        ----------
        image_path_iterator : Iterator[str]
            An iterator that yields the path to the next image to be saved.

        dynamic : bool, default: False
            Whether to save a static ``.png`` image or a ``.vtksz`` (interactive)
            file.

        Returns
        -------
        list[str]
            A list of the names of the images that were created.
        """
        image_names = []
        figures = pyvista.plotting.plotter._ALL_PLOTTERS
        for plotter in figures.values():
            _process_events_before_scraping(plotter)
            fname = next(image_path_iterator)
            # Make sure the extension is "png"
            fname_withoutextension, _ = os.path.splitext(fname)
            fname = fname_withoutextension + ".png"

            if hasattr(plotter, "_gif_filename"):
                # move gif to fname
                fname = fname[:-3] + "gif"
                shutil.move(plotter._gif_filename, fname)
                image_names.append(fname)
            else:
                plotter.screenshot(fname)
                if not dynamic or plotter.last_vtksz is None:
                    image_names.append(fname)
                else:  # pragma: no cover
                    fname = fname[:-3] + "vtksz"
                    with open(fname, "wb") as f:
                        f.write(plotter.last_vtksz)
                        image_names.append(fname)

        pyvista.close_all()  # close and clear all plotters
        return image_names
