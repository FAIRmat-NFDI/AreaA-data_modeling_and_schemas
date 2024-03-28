from readers import read_nexus_asc

# Replace 'testfile' with the name of your test file
result = read_nexus_asc('/home/brueckner/schemas/AreaA-data_modeling_and_schemas/transmission/transmission_plugin/uv_vis_nir_transmission_plugin/tests/data/3DM_test01.Probe.Raw.asc')

# Print the result to see what the function returns
print(result)