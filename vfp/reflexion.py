from driver import Cache
import llm

def reflect(x, e):
    return llm.generate(f"You are a Dafny programming language assistant.You are given some code and an error. Your goal is to write a few sentences to explain why the code is wrong as indicated by the error. You will need this as guidance when you try again later. Only provide the few sentence description in your answer, not the implementation. Reflect on the following code and error:\n{x}\n{e}\n")

class ReflexionCache(Cache):
    def previous_attempts(self, todo):
        r = ""
        if todo['name'] in self.cache:
            r = "\nPrevious reflections:\n"
            for m in self.cache[todo['name']]:
                r += f"{m}\n"
        return r

    def add(self, todo, x, e):
        if todo['name'] not in self.cache:
            self.cache[todo['name']] = []
        self.cache[todo['name']].append(reflect(x, e))

