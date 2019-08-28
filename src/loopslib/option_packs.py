"""Used to determine which optional packages belong to which 'pack' per release."""
# pylint: disable=too-many-locals
from pprint import pprint


class OptionPack(object):
    """Attributes for the 'collection packs' of packages in an Application."""
    def __init__(self, source, release, packages):
        self._source = source
        self._release = release.replace('.plist', '')

        self._content = self._source.get('Content', None)
        self._packages = packages

        self._optional_packages = set()

        # Only need packages that are truly optional.
        # Mandatory packages in these option packs _must_ be installed
        # anyway.
        for _pkg in self._packages:
            if not _pkg.IsMandatory:
                # _pkg_name = _pkg_name.replace('MAContent10_AssetPack_', '')
                self._optional_packages.add(_pkg)

        # In Logic Pro X & MainStage source files, the 'Content' key is a dict.
        # In the 'Content' dict, there's typically 'localised' versions, so pull
        # the 'en' one.
        if any(self._release.startswith(x) for x in ['logicpro', 'mainstage']):
            self._content = self._content.get('en')

        # Public attr.
        self.option_packs = self._process_packs()

    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-branches
    def _process_packs(self):
        """Processes the option packs."""
        # NOTE: Things get a little 'complicated' because Logic Pro X and MainStage
        # have 'subcontent' packs that make up _some_ of their bigger content packs.
        # So these are treated as 'packs' in their own right.
        result = list()

        if self._content:
            for _option_pack in self._content:
                _pack_name = _option_pack.get('Name', None)
                _pack_subc = _option_pack.get('SubContent', None)

                if not _pack_subc:  # No 'sub content' packages to worry about, i.e. GarageBand
                    _result = dict()  # Empty dict for results that meet our criteria of not 'IsMandatory'
                    _pkgs = set()  # Empty set to put package objects into

                    _option_pack_packages = _option_pack.get('Packages', None)

                    if _option_pack_packages:
                        for _package in _option_pack_packages:
                            for _package_obj in self._optional_packages:
                                if _package_obj.PackageName == _package:
                                    _pkgs.add(_package_obj)

                    if _pkgs:
                        _result[_pack_name] = _pkgs
                        result.append(_result)
                elif _pack_subc:  # Logic Pro X/MainStage 3 have opt packages that have sub packages
                    for _pack in _pack_subc:
                        _sub_pack_name = _pack.get('Name', None)
                        _result = dict()  # Empty dict for results that meet our criteria of not 'IsMandatory'
                        _pkgs = set()  # Empty set to put package objects into

                        _option_pack_packages = _pack.get('Packages', None)

                        if _option_pack_packages:
                            for _package in _option_pack_packages:
                                for _package_obj in self._optional_packages:
                                    if _package_obj.PackageName == _package:
                                        _pkgs.add(_package_obj)

                        if _pkgs:
                            _result[_sub_pack_name] = _pkgs
                            result.append(_result)
        # print(len(result))
        # pkgs = set()
        # for item in result:
        #     for k, v in item.items():
        #         for p in v:
        #             pkgs.add(p)
        # print(len(pkgs))

        return NotImplemented
    # pylint: enable=too-many-branches
    # pylint: enable=too-many-nested-blocks


class Pack(object):
    """Attributes for a specific option pack."""
    def __init__(self, **kwargs):
        _valid_kwargs = {'Name': None,
                         'Description': None,
                         'Packages': None,
                         'Release': None}

        for kwarg, value in _valid_kwargs.items():
            if kwarg in kwargs.keys():
                setattr(self, kwarg, kwargs.get(kwarg, None))
            else:
                setattr(self, kwarg, value)

    # pylint: disable=no-else-return
    # pylint: disable=no-member
    def __hash__(self):
        """Hash a tuple (immutable) containing the pack 'Name' attribute."""
        if isinstance(self, Pack):
            _pkgs = ', '.join(self.Packages)
            _str = '{} - {} - {} - {}'.format(self.Name,
                                              self.Description,
                                              _pkgs,
                                              self.Release)

            return hash(('Pack', _str))
        else:
            return NotImplemented

    def __eq__(self, other):
        """Used for testing equality of a pack instance based on the 'Name' attribute."""
        if isinstance(self, Pack):
            return (self.Name == other.Name and
                    self.Description == other.Description and
                    self.Packages == other.Packages and
                    self.Release == other.Release)
        else:
            return NotImplemented

    def __ne__(self, other):
        """Used for testing 'not' equality of a pack instance based on the 'Name' attribute.
        Implemented for Python 2.7 compatability."""
        if isinstance(self, Pack):
            return not (self.Name == other.Name and
                        self.Description == other.Description and
                        self.Packages == other.Packages and
                        self.Release == other.Release)
        else:
            return NotImplemented
    # pylint: enable=no-member
    # pylint: enable=no-else-return
# pylint: enable=too-many-locals
