# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: telemetry.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'telemetry.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftelemetry.proto\x12\tmarsrover\x1a\x1egoogle/protobuf/wrappers.proto\"\x0e\n\x0c\x45mptyRequest\"\x9a\x02\n\rTelemetryData\x12\x1b\n\x13ultrasound_distance\x18\x01 \x01(\x02\x12\x10\n\x08odometer\x18\x02 \x01(\x02\x12%\n\x08position\x18\x03 \x01(\x0b\x32\x13.marsrover.Position\x12\x0f\n\x07heading\x18\x04 \x01(\x02\x12*\n\x0bsearch_mode\x18\x05 \x01(\x0e\x32\x15.marsrover.SearchMode\x12,\n\x0fresources_found\x18\x06 \x03(\x0b\x32\x13.marsrover.Resource\x12\x15\n\rbattery_level\x18\x07 \x01(\x02\x12\x31\n\x0c\x63\x61mera_image\x18\x08 \x01(\x0b\x32\x1b.google.protobuf.BytesValue\" \n\x08Position\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\"?\n\x08Resource\x12\x0c\n\x04type\x18\x01 \x01(\t\x12%\n\x08location\x18\x02 \x01(\x0b\x32\x13.marsrover.Position*7\n\nSearchMode\x12\x13\n\x0fPATTERN_PURSUIT\x10\x00\x12\x14\n\x10RESOURCE_SEEKING\x10\x01\x32Z\n\x10TelemetryService\x12\x46\n\x0fStreamTelemetry\x12\x17.marsrover.EmptyRequest\x1a\x18.marsrover.TelemetryData0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'telemetry_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SEARCHMODE']._serialized_start=462
  _globals['_SEARCHMODE']._serialized_end=517
  _globals['_EMPTYREQUEST']._serialized_start=62
  _globals['_EMPTYREQUEST']._serialized_end=76
  _globals['_TELEMETRYDATA']._serialized_start=79
  _globals['_TELEMETRYDATA']._serialized_end=361
  _globals['_POSITION']._serialized_start=363
  _globals['_POSITION']._serialized_end=395
  _globals['_RESOURCE']._serialized_start=397
  _globals['_RESOURCE']._serialized_end=460
  _globals['_TELEMETRYSERVICE']._serialized_start=519
  _globals['_TELEMETRYSERVICE']._serialized_end=609
# @@protoc_insertion_point(module_scope)
