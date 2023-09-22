import wikigame.wikiapi.WikiApi

import scala.concurrent.ExecutionContext.Implicits.global
import sttp.client4.httpclient.HttpClientFutureBackend

import scala.concurrent._
import scala.concurrent.duration._

@main def main() =
  val backend = HttpClientFutureBackend()

  val response = WikiApi
    .sendRequest(
      backend,
      Map(
        "action" -> "query",
        "generator" -> "random",
        "grnlimit" -> "3",
        "grnnamespace" -> "0",
        "format" -> "json",
        "formatversion" -> "2"
      )
    )
    .map(response => {
      println(s"Got response code: ${response.code}")
      println(response.body)
    })

  Await.result(response, Duration(5000, MILLISECONDS))

  backend.close()
