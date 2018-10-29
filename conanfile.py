from conans import ConanFile, CMake, tools, Meson
import os

class GobjectintrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = "1.58.0"
    description = "GObject introspection is to describe the APIs and collect them in a uniform, machine readable format"
    url = "https://github.com/GNOME/gobject-introspection"
    homepage = "https://github.com/GNOME/gobject-introspection"
    license = "LGPLv2+,GPLv2+"
    exports = ["COPYING"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "libffi/3.3-rc0@conanos/dev","glib/2.58.0@conanos/dev"
    source_subfolder = "source_subfolder"

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.environment_append({"LD_LIBRARY_PATH":'%s/lib'%(self.deps_cpp_info["libffi"].rootpath)}):
            with tools.chdir(self.source_subfolder):
                meson = Meson(self)
                _defs = { 'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                          'cairo':'false', 'doctool':'true', 'gtk-doc': 'false',
                }
                meson.configure(
                    defs=_defs,
                    source_dir = '%s'%(os.getcwd()),
                    build_dir= '%s/builddir'%(os.getcwd()),
                    pkg_config_paths=['%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
                                      '%s/lib/pkgconfig'%(self.deps_cpp_info["glib"].rootpath)]
                    )
                meson.build(args=['-j2'])
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
