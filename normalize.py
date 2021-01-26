#!/usr/bin/env python3

import logging
import sys
import importlib
from google.protobuf.descriptor import FieldDescriptor


_INDENT = 2


def parse_method(mdesc, indent_level):
    mname = mdesc.name
    itdesc = mdesc.input_type
    itname = itdesc.name
    otdesc = mdesc.output_type
    otname = otdesc.name
    indent = ' ' * (_INDENT * indent_level)
    print(f'''{indent}rpc {mname} ({itname}) returns ({otname});''')


def parse_service(sdesc):
    sname = sdesc.name
    print(f'''service {sname} ''''{')
    mdescs = [mdesc for mdesc in sdesc.methods]
    mdescs.sort(key=lambda mdesc: mdesc.name)
    for mdesc in mdescs:
        parse_method(mdesc, 1)
    print('}')


def parse_enum(desc, indent_level):
    name = desc.name
    indent = ' ' * (_INDENT * indent_level)
    print(f'''{indent}enum {name} ''''{')

    vdescs = [vdesc for vdesc in desc.values]
    vdescs.sort(key=lambda vdesc: vdesc.number)
    indent = ' ' * (_INDENT * (indent_level + 1))
    for vdesc in vdescs:
        vname = vdesc.name
        vnum = vdesc.number
        print(f'''{indent}{vname} = {vnum};''')

    indent = ' ' * (_INDENT * indent_level)
    print(indent + '}')


_SCALAR_VALUE_TYPE_NAME_MAP = {
    FieldDescriptor.TYPE_BOOL: 'bool',
    FieldDescriptor.TYPE_BYTES: 'bytes',
    FieldDescriptor.TYPE_DOUBLE: 'double',
    FieldDescriptor.TYPE_ENUM: 'enum',
    FieldDescriptor.TYPE_FIXED32: 'fixed32',
    FieldDescriptor.TYPE_FIXED64: 'fixed64',
    FieldDescriptor.TYPE_FLOAT: 'float',
    FieldDescriptor.TYPE_GROUP: 'group',
    FieldDescriptor.TYPE_INT32: 'int32',
    FieldDescriptor.TYPE_INT64: 'int64',
    FieldDescriptor.TYPE_MESSAGE: 'message',
    FieldDescriptor.TYPE_SFIXED32: 'sfixed32',
    FieldDescriptor.TYPE_SFIXED64: 'sfixed64',
    FieldDescriptor.TYPE_SINT32: 'sint32',
    FieldDescriptor.TYPE_SINT64: 'sint64',
    FieldDescriptor.TYPE_STRING: 'string',
    FieldDescriptor.TYPE_UINT32: 'uint32',
    FieldDescriptor.TYPE_UINT64: 'uint64'
}


def parse_message(desc, indent_level):
    tname = desc.name
    indent = ' ' * (_INDENT * indent_level)
    print(f'''{indent}message {tname} ''''{')

    # メッセージ定義内のフィールドを名前の ASCII 順で表示．
    fdescs = [fdesc for fdesc in desc.fields]
    fdescs.sort(key=lambda fdesc: fdesc.index)
    indent = ' ' * (_INDENT * (indent_level + 1))
    for fdesc in fdescs:
        if fdesc.label == FieldDescriptor.LABEL_OPTIONAL:
            flabel = ''
        elif fdesc.label == FieldDescriptor.LABEL_REPEATED:
            flabel = 'repeated '
        elif fdesc.label == FieldDescriptor.LABEL_REQUIRED:
            flabel = 'required '
        else:
            raise RuntimeError(
                f'''{fdesc.label}: An unknown field label.''')

        if fdesc.message_type is not None:
            ftname = fdesc.message_type.name
        elif fdesc.enum_type is not None:
            ftname = fdesc.enum_type.name
        else:
            ftname = _SCALAR_VALUE_TYPE_NAME_MAP[fdesc.type]

        fname = fdesc.name
        fidx = fdesc.index
        print(f'''{indent}{flabel}{ftname} {fname} = {fidx};''')

    # メッセージ定義内の message 定義を名前の ASCII 順で表示．
    tdescs = [tdesc for tdesc in desc.nested_types]
    tdescs.sort(key=lambda tdesc: tdesc.name)
    for tdesc in tdescs:
        parse_message(tdesc, indent_level + 1)

    # メッセージ定義内の enum 定義を名前の ASCII 順で表示．
    edescs = [edesc for edescs in desc.enum_types]
    edescs.sort(key=lambda edesc: edesc.name)
    for edesc in edescs:
        parse_enum(edescs, indent_level + 1)

    if len(desc.enum_values_by_name) > 0:
        # TODO
        raise NotImplementedError()

    indent = ' ' * (_INDENT * indent_level)
    print(indent + '}')


def main() -> None:
    module_name = sys.argv[1]
    package = importlib.import_module(module_name)
    desc = package.DESCRIPTOR

    # .proto ファイル内の service 定義を名前の ASCII 順で表示．
    sdescs = [sdesc for sdesc in desc.services_by_name.values()]
    sdescs.sort(key=lambda sdesc: sdesc.name)
    for sdesc in sdescs:
        parse_service(sdesc)

    # .proto ファイル内の message 定義を名前の ASCII 順で表示．
    tdescs = [tdesc for tdesc in desc.message_types_by_name.values()]
    tdescs.sort(key=lambda tdesc: tdesc.name)
    for tdesc in tdescs:
        parse_message(tdesc, 0)

    # .proto ファイル内の enum 定義を名前の ASCII 順で表示．
    for edesc in desc.enum_types_by_name.values():
        parse_enum(edesc, 0)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        logging.exception('Abort with an exception.')
        sys.exit(1)
