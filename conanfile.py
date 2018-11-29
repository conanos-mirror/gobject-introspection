from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os

class GobjectintrospectionConan(ConanFile):
    name = "gobject-introspection"
    version = "1.58.1"
    description = "GObject introspection is to describe the APIs and collect them in a uniform, machine readable format"
    url = "https://github.com/GNOME/gobject-introspection"
    homepage = "https://github.com/GNOME/gobject-introspection"
    license = "LGPLv2+,GPLv2+"
    exports = ["COPYING"]
    generators = "gcc","visual_studio"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': False, 'fPIC': True }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    
    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")

        config_scheme(self)
    
    def build_requirements(self):
        self.build_requires("zlib/1.2.11@conanos/stable")
        self.build_requires("libffi/3.299999@conanos/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        url_="https://github.com/GNOME/gobject-introspection/archive/{version}.tar.gz".format(version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["glib","zlib"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        libpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "lib") for i in ["glib"] ]
        meson = Meson(self)
        if self.settings.os == "Linux":
            with tools.environment_append({
                'LD_LIBRARY_PATH' : os.pathsep.join(libpath),
                'PKG_CONFIG_PATH' : os.pathsep.join(pkg_config_paths),
                }):
                meson.configure(defs={'prefix' : prefix, 'libdir':'lib'},
                                source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                                pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))
        
        if self.settings.os == "Windows":
            binpath=[ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["glib","zlib","libffi"] ]
            include = [os.path.join(self.deps_cpp_info["glib"].rootpath, "include")]
            pkg_config_paths.extend([ os.path.join(self.deps_cpp_info["libffi"].rootpath, "lib", "pkgconfig") ])
            with tools.environment_append({
                'PATH' : os.pathsep.join(binpath + [os.getenv('PATH')]),
                'INCLUDE' : os.pathsep.join([os.getenv('INCLUDE')]+include),
                'PKG_CONFIG_PATH' : os.pathsep.join(pkg_config_paths),
                }):
                meson.configure(defs={'prefix' : prefix},
                                source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                                pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
