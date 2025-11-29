import tornado.escape
from bson import ObjectId
from backend.db import tasks
from backend.handlers.auth import BaseHandler
import datetime

class TasksHandler(BaseHandler):
    async def get(self):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        cursor = tasks.find()
        out = []
        async for t in cursor:
            out.append({
                "id": str(t["_id"]),
                "text": t["text"],
                "user": t["user"],
                "date": t["date"]
            })

        return self.write_json({"items": out})

    async def post(self):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        body = tornado.escape.json_decode(self.request.body)
        text = body.get("text", "").strip()
        x = datetime.datetime.now()
        formatted_time = x.strftime("%Y-%m-%d %H:%M")
        if not text:
            return self.write_json({"error": "Testo obbligatorio"}, 400)

        result = await tasks.insert_one({
            "user_id": ObjectId(user["id"]),
            "text": text,
            "user": user["email"],
            "date": formatted_time
        })

        return self.write_json({"id": str(result.inserted_id)}, 201)



class TaskDeleteHandler(BaseHandler):
    async def delete(self, task_id):
        user = self.get_current_user()
        if not user:
            return self.write_json({"error": "Non autenticato"}, 401)

        await tasks.delete_one({
            "_id": ObjectId(task_id),
            "user_id": ObjectId(user["id"])
        })

        return self.write_json({"message": "Eliminato"})
