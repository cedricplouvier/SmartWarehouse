# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: KeepAlive.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='KeepAlive.proto',
  package='message.alive',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0fKeepAlive.proto\x12\rmessage.alive\"6\n\x05\x41live\x12\n\n\x02id\x18\x01 \x01(\x05\x12!\n\x04type\x18\x02 \x01(\x0e\x32\x13.message.alive.Type*\x1b\n\x04Type\x12\t\n\x05ROBOT\x10\x00\x12\x08\n\x04NODE\x10\x01\x62\x06proto3'
)

_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='message.alive.Type',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ROBOT', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='NODE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=90,
  serialized_end=117,
)
_sym_db.RegisterEnumDescriptor(_TYPE)

Type = enum_type_wrapper.EnumTypeWrapper(_TYPE)
ROBOT = 0
NODE = 1



_ALIVE = _descriptor.Descriptor(
  name='Alive',
  full_name='message.alive.Alive',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='message.alive.Alive.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='message.alive.Alive.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=34,
  serialized_end=88,
)

_ALIVE.fields_by_name['type'].enum_type = _TYPE
DESCRIPTOR.message_types_by_name['Alive'] = _ALIVE
DESCRIPTOR.enum_types_by_name['Type'] = _TYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Alive = _reflection.GeneratedProtocolMessageType('Alive', (_message.Message,), {
  'DESCRIPTOR' : _ALIVE,
  '__module__' : 'KeepAlive_pb2'
  # @@protoc_insertion_point(class_scope:message.alive.Alive)
  })
_sym_db.RegisterMessage(Alive)


# @@protoc_insertion_point(module_scope)