# # Helper: create a zip of the project (for convenience)
# import zipfile, os
# proj = '/mnt/data/agentic_doc_extractor'
# zip_name = proj + '.zip'
# with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as z:
#     for root, dirs, files in os.walk(proj):
#         for fn in files:
#             path = os.path.join(root, fn)
#             z.write(path, arcname=os.path.relpath(path, proj))
# print('Created', zip_name)
