Feature Branch: Image-analysis
Objective: Build the Image-analysis package to be invoked by the tool call orchestrator.

Independent testing steps
FOLLOW THE INSTRUCTIONS -

pip install -r requirements.txt
docker pull qdrant/qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
-v $(pwd)/qdrant_storage:/qdrant/storage \
 --name qdrant \
 qdrant/qdrant
 curl http://localhost:6333/collections

 GO TO http://localhost:8000/ 
 then
 http://localhost:3000/docs
